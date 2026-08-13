#!/usr/bin/env python3
"""Run the offline Pathview Plus audit and create machine-readable evidence."""

from __future__ import annotations

import csv
import json
import os
import platform
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
JUNIT = RESULTS / "junit.xml"
PYTEST_LOG = RESULTS / "pytest-output.txt"
ID_PATTERN = re.compile(r"PV-(?:BUG|FEATURE)-\d{3}")


HIGH_PRIORITY = {
    "PV-BUG-004",  # cache cannot bypass species service
    "PV-BUG-006",  # map_null contract
    "PV-BUG-008",  # core/highlighting result mismatch
    "PV-BUG-009",  # missing mapping identifier
    "PV-BUG-012",  # advertised aggregations crash
    "PV-BUG-023",  # standard SBGN empty
    "PV-BUG-029",  # compound coordinate system
    "PV-BUG-030",  # compound dimensions
    "PV-BUG-034",  # native dimensions
    "PV-BUG-038",  # PDF loses states
    "PV-BUG-039",  # highlights miss nodes
    "PV-BUG-045",  # documented spline NaNs
    "PV-BUG-052",  # compound-only CLI crash
    "PV-BUG-058",  # MyGene endpoint
    "PV-BUG-065",  # HTML accepted as SBGN
    "PV-BUG-074",  # Reactome route
    "PV-BUG-075",  # symbols do not update label
    "PV-FEATURE-003",  # SVG no relations
    "PV-FEATURE-004",  # PDF no relations
    "PV-FEATURE-007",  # non-KEGG not connected
}


def command_output(command: list[str], cwd: Path | None = None) -> str | None:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True,
            timeout=15,
        ).stdout.strip()
    except Exception:
        return None


def record_environment() -> dict:
    import pathview
    import polars

    package_file = Path(pathview.__file__).resolve()
    source_root = package_file.parent.parent
    info = {
        "audit_date": datetime.now().astimezone().isoformat(),
        "platform": platform.platform(),
        "python": sys.version,
        "executable": sys.executable,
        "pathview_distribution_version": version("pathview-plus"),
        "pathview_runtime_version": pathview.__version__,
        "pathview_package_file": str(package_file),
        "pathview_source_root": str(source_root),
        "pathview_commit": command_output(["git", "rev-parse", "HEAD"], source_root),
        "pathview_commit_summary": command_output(
            ["git", "log", "-1", "--format=%h %cs %s"], source_root
        ),
        "pytest": version("pytest"),
        "polars": polars.__version__,
        "numpy": version("numpy"),
        "matplotlib": version("matplotlib"),
        "pillow": version("Pillow"),
        "network_mode": "offline; integrations use controlled mock responses",
    }
    (RESULTS / "environment.json").write_text(
        json.dumps(info, indent=2) + "\n", encoding="utf-8"
    )
    return info


def run_pytest() -> int:
    env = os.environ.copy()
    env.update(
        {
            "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": str(RESULTS / ".matplotlib"),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        "pytest.ini",
        "tests",
        "-ra",
        "--tb=short",
        "--junitxml",
        str(JUNIT),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    PYTEST_LOG.write_text(completed.stdout, encoding="utf-8")
    print(completed.stdout)
    return completed.returncode


def parse_junit() -> tuple[list[dict], dict]:
    root = ET.parse(JUNIT).getroot()
    cases: list[dict] = []
    for case in root.iter("testcase"):
        name = case.attrib.get("name", "")
        classname = case.attrib.get("classname", "")
        duration = float(case.attrib.get("time", 0.0))
        message = ""
        status = "PASS"
        child = next(iter(case), None)
        if child is not None:
            message = child.attrib.get("message", "") or (child.text or "").splitlines()[0]
            if child.tag == "skipped":
                finding_id_match = ID_PATTERN.search(message)
                if finding_id_match:
                    status = (
                        "FEATURE_GAP"
                        if finding_id_match.group().startswith("PV-FEATURE")
                        else "KNOWN_BUG"
                    )
                else:
                    status = "NOT_RUN"
            elif child.tag == "failure":
                status = "FAIL"
            elif child.tag == "error":
                status = "ERROR"
        finding_match = ID_PATTERN.search(message)
        cases.append(
            {
                "test": f"{classname}::{name}",
                "status": status,
                "finding_id": finding_match.group() if finding_match else None,
                "message": message,
                "seconds": duration,
            }
        )

    counts = Counter(case["status"] for case in cases)
    unique = {case["finding_id"] for case in cases if case["finding_id"]}
    summary = {
        "total_test_cases": len(cases),
        "status_counts": dict(sorted(counts.items())),
        "unique_reproduced_findings": len(unique),
        "unique_confirmed_bug_ids": len([item for item in unique if item.startswith("PV-BUG")]),
        "unique_feature_gap_ids": len(
            [item for item in unique if item.startswith("PV-FEATURE")]
        ),
        "unexpected_failures": counts.get("FAIL", 0) + counts.get("ERROR", 0),
        "total_seconds": round(sum(case["seconds"] for case in cases), 3),
    }
    return cases, summary


def write_case_results(cases: list[dict], summary: dict, environment: dict) -> None:
    payload = {"summary": summary, "environment": environment, "tests": cases}
    (RESULTS / "audit-results.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    with (RESULTS / "audit-results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(cases[0]))
        writer.writeheader()
        writer.writerows(cases)

    findings: dict[str, dict] = {}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for case in cases:
        if case["finding_id"]:
            grouped[case["finding_id"]].append(case)
    for finding_id in sorted(grouped):
        group = grouped[finding_id]
        reason = group[0]["message"]
        reason = reason.split(":", 1)[1].strip() if ":" in reason else reason
        findings[finding_id] = {
            "id": finding_id,
            "kind": "feature_gap" if finding_id.startswith("PV-FEATURE") else "reproduced_bug",
            "priority": "P1" if finding_id in HIGH_PRIORITY else "P2/P3",
            "summary": reason,
            "reproduced": True,
            "test_case_count": len(group),
            "tests": [case["test"] for case in group],
        }
    (ROOT / "BUGS.json").write_text(
        json.dumps(
            {
                "scope": "Pathview Plus commit " + str(environment.get("pathview_commit")),
                "generated": environment["audit_date"],
                "important_note": (
                    "These are reproducible engineering findings with different priorities; "
                    "feature gaps are separated from code defects and live service observations."
                ),
                "counts": {
                    "reproduced_bug_ids": summary["unique_confirmed_bug_ids"],
                    "feature_gap_ids": summary["unique_feature_gap_ids"],
                },
                "findings": list(findings.values()),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_findings_markdown() -> None:
    data = json.loads((ROOT / "BUGS.json").read_text(encoding="utf-8"))
    findings = data["findings"]
    lines = [
        "# Every finding from my Pathview Plus checks",
        "",
        "This is my complete list from the test run. I kept this page because the shorter",
        "report only talks about the biggest patterns, while this table shows every finding",
        "and the exact test that reproduced it.",
        "",
        "I split the list into two groups. P1 contains the things I think should be checked",
        "first because they affect a main workflow or an advertised feature. P2/P3 contains",
        "smaller issues, input checks, and edge cases. A feature gap is listed separately",
        "from a reproduced bug because it can mean that a feature was started but is not",
        "connected yet.",
        "",
        "## Totals",
        "",
        f"- Different reproduced findings: **{data['counts']['reproduced_bug_ids']}**",
        f"- Different feature gaps: **{data['counts']['feature_gap_ids']}**",
        "",
    ]
    for priority, heading in (("P1", "P1 — findings I would look at first"), ("P2/P3", "P2/P3 — smaller issues and edge cases")):
        lines.extend(
            [
                f"## {heading}",
                "",
                "| ID | Type | What I reproduced | Exact test(s) |",
                "|---|---|---|---|",
            ]
        )
        for item in findings:
            if item["priority"] != priority:
                continue
            summary = item["summary"].replace("|", "\\|").replace("\n", " ")
            tests = "<br>".join(f"`{test}`" for test in item["tests"])
            kind = (
                "feature gap"
                if item["kind"] == "feature_gap"
                else "reproduced finding"
            )
            lines.append(
                f"| {item['id']} | {kind} | {summary} | {tests} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Files I used for this list",
            "",
            "If someone wants to check a row or use the results in another program:",
            "",
            "- `BUGS.json` has the same list in a machine-readable format.",
            "- `results/audit-results.csv` has every test case, including the ones that passed.",
            "- `results/junit.xml` can be used by continuous-integration tools.",
            "- `results/pytest-output.txt` has the full warnings and traceback summaries.",
            "",
        ]
    )
    (ROOT / "ALL-FINDINGS.md").write_text("\n".join(lines), encoding="utf-8")


def run_evidence_generator() -> int:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_evidence.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": str(RESULTS / ".matplotlib"),
        },
    )
    (RESULTS / "evidence-generation.txt").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.stdout:
        print(completed.stdout)
    if completed.stderr:
        print(completed.stderr, file=sys.stderr)
    return completed.returncode


def run_notebook_builder() -> int:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_notebook.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "MPLBACKEND": "Agg",
            "MPLCONFIGDIR": str(RESULTS / ".matplotlib"),
        },
    )
    (RESULTS / "notebook-build.txt").write_text(
        completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.stdout:
        print(completed.stdout)
    if completed.stderr:
        print(completed.stderr, file=sys.stderr)
    return completed.returncode


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    print("Pathview Plus deep bug checks")
    print(f"Audit folder: {ROOT}")
    environment = record_environment()
    pytest_code = run_pytest()
    if not JUNIT.exists():
        print("ERROR: pytest did not create JUnit evidence", file=sys.stderr)
        return pytest_code or 2
    cases, summary = parse_junit()
    write_case_results(cases, summary, environment)
    write_findings_markdown()
    evidence_code = run_evidence_generator()
    (RESULTS / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print("\nAudit summary")
    print(json.dumps(summary, indent=2))
    if summary["unexpected_failures"]:
        return pytest_code or 1
    if evidence_code:
        return evidence_code
    return run_notebook_builder()


if __name__ == "__main__":
    raise SystemExit(main())
