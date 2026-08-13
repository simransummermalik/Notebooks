#!/usr/bin/env python3
"""Build the August 12 old-vs-new Pathview Plus comparison artifacts."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DAY = Path(__file__).resolve().parents[1]
DATA = DAY / "data"
RESULTS = DAY / "results"
TABLES = RESULTS / "tables"
FIGURES = RESULTS / "figures"
PROOF = RESULTS / "proof"
KEY = DAY / "outputs-that-matter"

OLD_FINDINGS_PATH = DATA / "august-10-findings.json"
OLD_TEST_SUMMARY_PATH = DATA / "august-10-test-summary.json"
NEW_STATUS_PATH = DATA / "v3-findings-status-source.json"

OLD_COMMIT = "07aee813375347bcc933ad21b4aed561dd7cd3bf"
NEW_COMMIT = "d4d45decec56e1ebec15cf04ae62ff944851780e"
STATUS_ORDER = ["fixed", "still_reproducible", "changed"]
STATUS_LABEL = {
    "fixed": "Fixed",
    "still_reproducible": "Still reproducible",
    "changed": "Changed interface/behavior",
}
STATUS_COLOR = {
    "fixed": "#2E8B57",
    "still_reproducible": "#C94C4C",
    "changed": "#D69E2E",
}
CHANGED_EVIDENCE = {
    "PV-BUG-005": "v3 uses separate `ColorScale`, `gene_color`, and `cpd_color` settings. A fair follow-up is to test partial settings through the new scale API.",
    "PV-BUG-016": "The `entrez_gnodes` switch was removed; identifiers are normalized while KGML is parsed and mapping uses `kegg_names`. A fair follow-up is to test prefixed and unprefixed KEGG IDs through the new mapper.",
    "PV-BUG-018": "String-valued columns are excluded from numeric color mapping instead of being interpreted as hexadecimal values. A fair follow-up is to decide whether numeric strings should be rejected or explicitly coerced.",
    "PV-BUG-047": "Obstacle handling is now the documented `routing_mode='avoid'` path. A fair follow-up is to test that mode with a supplied obstacle.",
    "PV-BUG-067": "The `render_mode` argument now selects native, vector, graph, or SVG behavior. A fair follow-up is to run SVG mode with KGML present and no PNG.",
    "PV-BUG-077": "The old CLI `--simulate` branch was removed; simulation remains available through Python data-generation functions. There is no like-for-like CLI call to recheck.",
    "PV-FEATURE-007": "Non-KEGG work now uses `sbgnview()` and `sbgnview_batch()` rather than dispatching through `pathview()`. A fair follow-up is to test download, parse, map, and render through that entry point.",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def status_lookup(classifications: dict[str, list[str]]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for status, ids in classifications.items():
        for finding_id in ids:
            if finding_id in lookup:
                raise AssertionError(f"Duplicate classification for {finding_id}")
            lookup[finding_id] = status
    return lookup


def build_rows(old: dict, new: dict) -> list[dict[str, object]]:
    lookup = status_lookup(new["classifications"])
    evidence = new["adapted_recheck_evidence"]
    old_ids = {item["id"] for item in old["findings"]}
    assert old_ids == set(lookup), "Old and new finding IDs must match exactly"
    assert not new["classifications"]["not_retested"]

    rows = []
    for item in old["findings"]:
        status = lookup[item["id"]]
        rows.append(
            {
                "id": item["id"],
                "old_priority": item["priority"],
                "old_kind": item["kind"],
                "old_summary": item["summary"],
                "v3_status": status,
                "v3_status_label": STATUS_LABEL[status],
                "v3_evidence": evidence.get(
                    item["id"],
                    CHANGED_EVIDENCE.get(
                        item["id"],
                        "The old failure condition is absent in the v3 test, adapted recheck, or direct source audit.",
                    ),
                ),
                "old_test_case_count": item["test_case_count"],
                "old_tests": "; ".join(item["tests"]),
            }
        )
    return rows


def write_tables(rows: list[dict[str, object]]) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with (TABLES / "all-86-findings.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    write_json(TABLES / "all-86-findings.json", rows)

    for status in STATUS_ORDER:
        selected = [row for row in rows if row["v3_status"] == status]
        filename = {
            "fixed": "fixed-60.csv",
            "still_reproducible": "remaining-19.csv",
            "changed": "changed-7.csv",
        }[status]
        with (TABLES / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(selected)


def build_summary(rows: list[dict[str, object]], old_tests: dict) -> dict:
    status_counts = Counter(row["v3_status"] for row in rows)
    priority_status = defaultdict(Counter)
    kind_status = defaultdict(Counter)
    for row in rows:
        priority_status[row["old_priority"]][row["v3_status"]] += 1
        kind_status[row["old_kind"]][row["v3_status"]] += 1

    summary = {
        "comparison_date": "2026-08-12",
        "old_snapshot": {
            "commit": OLD_COMMIT,
            "distribution_version": "2.0.2",
            "runtime_version": "2.0.0",
            "audit_date": "2026-08-10",
            "unique_findings": len(rows),
            "test_run": old_tests,
        },
        "new_snapshot": {
            "commit": NEW_COMMIT,
            "package_version": "3.1.0",
            "source_commit_date": "2026-08-11",
            "upstream_test_run": {
                "collected": 327,
                "passed": 321,
                "skipped": 6,
                "failed": 0,
            },
        },
        "classification_counts": {
            "total": len(rows),
            "fixed": status_counts["fixed"],
            "still_reproducible": status_counts["still_reproducible"],
            "changed": status_counts["changed"],
            "not_retested": 0,
        },
        "classification_percentages": {
            key: round(100 * status_counts[key] / len(rows), 1) for key in STATUS_ORDER
        },
        "priority_by_status": {
            priority: {status: counts[status] for status in STATUS_ORDER}
            for priority, counts in priority_status.items()
        },
        "old_kind_by_status": {
            kind: {status: counts[status] for status in STATUS_ORDER}
            for kind, counts in kind_status.items()
        },
        "remaining_p1_ids": [
            row["id"]
            for row in rows
            if row["old_priority"] == "P1" and row["v3_status"] == "still_reproducible"
        ],
        "changed_ids": [row["id"] for row in rows if row["v3_status"] == "changed"],
        "comparison_note": (
            "The 239 August 10 outcomes and the 327 v3 outcomes come from different "
            "suites and cannot be read as before-and-after pass rates. The comparable "
            "denominator is the same 86 unique August 10 findings, each assigned one "
            "current status."
        ),
    }
    assert summary["classification_counts"] == {
        "total": 86,
        "fixed": 60,
        "still_reproducible": 19,
        "changed": 7,
        "not_retested": 0,
    }
    assert summary["priority_by_status"]["P1"] == {
        "fixed": 14,
        "still_reproducible": 5,
        "changed": 1,
    }
    assert summary["priority_by_status"]["P2/P3"] == {
        "fixed": 46,
        "still_reproducible": 14,
        "changed": 6,
    }
    write_json(RESULTS / "comparison-summary.json", summary)
    return summary


def style_axes(axis) -> None:
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0)
    axis.grid(axis="x", color="#E2E8F0", linewidth=0.8)
    axis.set_axisbelow(True)


def make_status_chart(summary: dict) -> None:
    counts = summary["classification_counts"]
    labels = [STATUS_LABEL[status] for status in STATUS_ORDER]
    values = [counts[status] for status in STATUS_ORDER]
    colors = [STATUS_COLOR[status] for status in STATUS_ORDER]
    fig, axis = plt.subplots(figsize=(10, 5.8))
    bars = axis.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.55)
    for bar, value in zip(bars, values[::-1]):
        axis.text(value + 1, bar.get_y() + bar.get_height() / 2, str(value), va="center", fontsize=13)
    axis.set_xlim(0, 66)
    axis.set_xlabel("Unique findings (not test cases)")
    fig.suptitle(
        "Disposition of the 86 August 10 findings",
        x=0.24,
        y=0.97,
        ha="left",
        fontsize=17,
        weight="bold",
    )
    fig.text(0.24, 0.90, "Old distribution 2.0.2 / runtime 2.0.0 (07aee81) → v3.1.0 (d4d45de)", color="#4A5568")
    style_axes(axis)
    fig.subplots_adjust(left=0.24, right=0.96, bottom=0.14, top=0.79)
    fig.savefig(FIGURES / "01-overall-status.png", dpi=180, facecolor="white")
    plt.close(fig)


def make_priority_chart(summary: dict) -> None:
    priority = summary["priority_by_status"]
    groups = ["P1", "P2/P3"]
    fig, axis = plt.subplots(figsize=(10, 5.8))
    left = [0, 0]
    for status in STATUS_ORDER:
        values = [priority[group][status] for group in groups]
        bars = axis.barh(groups, values, left=left, color=STATUS_COLOR[status], label=STATUS_LABEL[status])
        for bar, value, offset in zip(bars, values, left):
            if value:
                axis.text(offset + value / 2, bar.get_y() + bar.get_height() / 2, str(value), ha="center", va="center", color="white", weight="bold")
        left = [left[index] + values[index] for index in range(2)]
    axis.invert_yaxis()
    axis.set_xlabel("")
    fig.text(0.525, 0.045, "Unique August 10 findings", ha="center")
    fig.suptitle("Results by original August 10 priority", x=0.08, y=0.97, ha="left", fontsize=17, weight="bold")
    axis.legend(frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(0.0, 1.02))
    style_axes(axis)
    fig.subplots_adjust(left=0.08, right=0.97, bottom=0.14, top=0.79)
    fig.savefig(FIGURES / "02-priority-status.png", dpi=180, facecolor="white")
    plt.close(fig)


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def fit_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    fitted = image.copy().convert("RGB")
    fitted.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "white")
    x = (size[0] - fitted.width) // 2
    y = (size[1] - fitted.height) // 2
    canvas.paste(fitted, (x, y))
    return canvas


def make_visual_comparison() -> dict:
    old_path = DATA / "old-v2-half-half.png"
    new_path = DATA / "new-v3-half-half.png"
    old = Image.open(old_path).convert("RGB")
    new = Image.open(new_path).convert("RGB")
    same_dimensions = old.size == new.size
    difference = ImageChops.difference(old, new) if same_dimensions else None
    changed_pixels = None
    if difference is not None:
        pixels = difference.get_flattened_data() if hasattr(difference, "get_flattened_data") else difference.getdata()
        changed_pixels = sum(pixel != (0, 0, 0) for pixel in pixels)

    panel_size = (780, 600)
    margin = 35
    header = 110
    footer = 80
    canvas = Image.new("RGB", (panel_size[0] * 2 + margin * 3, panel_size[1] + header + footer), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 22), "Half-and-half workflow on frozen hsa04110", fill="#1A202C", font=font(32, True))
    draw.text((margin, 64), "Saved raw overlays • three shared Entrez IDs and values • condition labels differ", fill="#4A5568", font=font(20))
    positions = [margin, margin * 2 + panel_size[0]]
    for x, image, title, subtitle in [
        (positions[0], old, "Old snapshot", "distribution 2.0.2 / runtime 2.0.0 • 07aee81"),
        (positions[1], new, "New snapshot", "Pathview Plus 3.1.0 • d4d45de"),
    ]:
        fitted = fit_image(image, panel_size)
        canvas.paste(fitted, (x, header))
        draw.rectangle((x, header, x + panel_size[0], header + panel_size[1]), outline="#CBD5E0", width=2)
        draw.text((x, header + panel_size[1] + 12), title, fill="#1A202C", font=font(24, True))
        draw.text((x, header + panel_size[1] + 43), subtitle, fill="#4A5568", font=font(17))
    canvas.save(FIGURES / "03-old-vs-new-half-half.png", quality=95)

    metrics = {
        "old_image": {"path": str(old_path.relative_to(DAY)), "size": list(old.size), "sha256": sha256(old_path)},
        "new_image": {"path": str(new_path.relative_to(DAY)), "size": list(new.size), "sha256": sha256(new_path)},
        "same_dimensions": same_dimensions,
        "changed_pixels": changed_pixels,
        "changed_pixel_fraction": round(changed_pixels / (old.width * old.height), 6) if changed_pixels is not None else None,
        "interpretation": (
            "The two saved raw rasters both show the two-condition left/right node split and both are 1039 x 801. "
            "This does not test the dimensions of the public Matplotlib-composed native output, so it does not resolve PV-BUG-034."
        ),
    }
    write_json(TABLES / "half-half-image-metrics.json", metrics)
    return metrics


def md_escape(value: object) -> str:
    return html.escape(str(value).replace("\n", " "), quote=False).replace("|", "\\|")


def write_finding_reports(rows: list[dict[str, object]], summary: dict) -> None:
    REPORTS = DAY / "reports"
    REPORTS.mkdir(parents=True, exist_ok=True)

    full_lines = [
        "# Status of all 86 findings from the August 10 Pathview Plus audit",
        "",
        "## Scope and how to read this table",
        "",
        "This is a follow-up to the August 10 audit, not a new search for every possible Pathview Plus defect. It follows the same 86 unique finding IDs from commit `07aee813` (distribution `2.0.2`; runtime version string `2.0.0`) and checks their current equivalent at Pathview Plus `3.1.0`, commit `d4d45de`. Every ID received exactly one status.",
        "",
        "The P1/P2-P3 labels are the original August 10 triage labels. P1 referred to a main workflow or advertised feature; P2/P3 covered lower-priority validation issues, API boundaries, and edge cases. The labels were not reassigned for v3.",
        "",
        "| v3 status | Count | Definition used in this comparison |",
        "|---|---:|---|",
        "| Fixed | 60 | The old failure condition was absent in a current v3 test, adapted check, or source review. |",
        "| Still reproducible | 19 | A current equivalent still showed the underlying behavior. |",
        "| Changed interface/behavior | 7 | The old contract was replaced, so the old reproducer is neither a fair pass nor a fair fail. |",
        "| **Total** | **86** | One row for each unique August 10 finding. |",
        "",
        "Use this page as the index. Current reproduction details are in `REMAINING-19.md`; replacement contracts are in `CHANGED-7.md`; the 60 rows whose old condition was absent are in `FIXED-60.md`.",
        "",
        "| ID | August 10 priority | August 10 description | Result at v3.1.0 |",
        "|---|---|---|---|",
    ]
    for row in rows:
        full_lines.append(
            f"| `{row['id']}` | {row['old_priority']} | {md_escape(row['old_summary'])} | {row['v3_status_label']} |"
        )
    (REPORTS / "ALL-86-FINDINGS.md").write_text("\n".join(full_lines) + "\n", encoding="utf-8")

    remaining = [row for row in rows if row["v3_status"] == "still_reproducible"]
    remaining_lines = [
        "# Nineteen August 10 findings still reproduced in Pathview Plus 3.1.0",
        "",
        "I rewrote these checks only where necessary to use the v3 interface. In each row, the old problem is shown next to what the current check produced. A row can stay here after a partial improvement; for example, XML response validation improved for `PV-BUG-057`, but mocked HTML was still accepted as a PNG.",
        "",
        "## Five original P1 findings",
        "",
        "P1 is the original August 10 triage label, not a newly calculated v3 severity score.",
        "",
        "| ID | August 10 problem | What the v3.1.0 recheck produced |",
        "|---|---|---|",
    ]
    for row in remaining:
        if row["old_priority"] == "P1":
            remaining_lines.append(f"| `{row['id']}` | {md_escape(row['old_summary'])} | {md_escape(row['v3_evidence'])} |")
    remaining_lines.extend(
        [
            "",
            "## Fourteen original P2/P3 findings",
            "",
            "These rows cover validation boundaries, parser information loss, and integration details rather than only visible crashes.",
            "",
            "| ID | August 10 problem | What the v3.1.0 recheck produced |",
            "|---|---|---|",
        ]
    )
    for row in remaining:
        if row["old_priority"] != "P1":
            remaining_lines.append(f"| `{row['id']}` | {md_escape(row['old_summary'])} | {md_escape(row['v3_evidence'])} |")
    (REPORTS / "REMAINING-19.md").write_text("\n".join(remaining_lines) + "\n", encoding="utf-8")

    changed = [row for row in rows if row["v3_status"] == "changed"]
    changed_lines = [
        "# Seven findings reclassified because v3 replaced the relevant interface",
        "",
        "These seven are not part of the 60 fixed or the 19 still reproducible rows. In each case, v3.1.0 removed or replaced the argument, command, or dispatch path used by the old reproducer. I recorded what v3 uses instead without treating the replacement itself as proof that it is correct.",
        "",
        "| ID | August 10 problem | What v3.1.0 uses instead / fair follow-up |",
        "|---|---|---|",
    ]
    for row in changed:
        changed_lines.append(f"| `{row['id']}` | {md_escape(row['old_summary'])} | {md_escape(row['v3_evidence'])} |")
    (REPORTS / "CHANGED-7.md").write_text("\n".join(changed_lines) + "\n", encoding="utf-8")

    fixed = [row for row in rows if row["v3_status"] == "fixed"]
    fixed_lines = [
        "# Sixty August 10 failure conditions not reproduced in Pathview Plus 3.1.0",
        "",
        "These 60 IDs were classified Fixed in the v3.1.0 recheck. Fixed is narrow here: the exact old failure condition was absent at commit `d4d45de`, based on a current test, an adapted check, or source inspection. It is not a claim that the entire surrounding feature is defect-free. Fourteen of these were original P1 findings and 46 were P2/P3.",
        "",
        "Examples include offline cached species resolution (`PV-BUG-004`), a composable result with identifiers and aligned highlights (`PV-BUG-008`, `PV-BUG-009`, `PV-BUG-039`), namespace-aware SBGN parsing (`PV-BUG-023`), corrected compound geometry (`PV-BUG-029` through `PV-BUG-031`), edges in SVG and graph outputs (`PV-FEATURE-003`, `PV-FEATURE-004`), and compound-only CLI input (`PV-BUG-052`).",
        "",
        "| ID | August 10 priority | Failure condition that was absent in v3.1.0 |",
        "|---|---|---|",
    ]
    for row in fixed:
        fixed_lines.append(f"| `{row['id']}` | {row['old_priority']} | {md_escape(row['old_summary'])} |")
    (REPORTS / "FIXED-60.md").write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")

    assert len(fixed) == summary["classification_counts"]["fixed"]
    assert len(remaining) == summary["classification_counts"]["still_reproducible"]
    assert len(changed) == summary["classification_counts"]["changed"]


def copy_key_evidence() -> None:
    sources = {
        KEY / "figures/04-old-compound-coordinate-bug.png": ROOT / "08-10-2026/pathveiw bug checks/results/evidence/02-compound-coordinate-reproduction.png",
        KEY / "figures/05-new-gene-and-compound.png": ROOT / "08-11-2026/results/python-pathview/figures/hsa00020.python-gene-compound-figure.png",
        KEY / "figures/06-old-svg-missing-edges.svg": ROOT / "08-10-2026/pathveiw bug checks/results/evidence/official-hsa04110/hsa04110.half-and-half.svg",
        KEY / "figures/07-new-svg-with-edges.svg": ROOT / "08-11-2026/results/python-pathview/figures/hsa04110.python-mode-svg-svg.svg",
        KEY / "figures/08-new-working-highlights.png": ROOT / "08-11-2026/results/python-pathview/figures/hsa04110.python-highlighted.png",
        KEY / "figures/09-new-namespaced-sbgn.svg": ROOT / "08-11-2026/results/sbgnview/P00001.namespaced.python-two-state.svg",
        KEY / "figures/10-new-graph-mode-current-output.png": ROOT / "08-11-2026/results/python-pathview/figures/hsa04110.python-mode-graph-png.png",
        KEY / "proof/01-august-10-bug-list.json": ROOT / "08-10-2026/pathveiw bug checks/BUGS.json",
        KEY / "proof/02-august-10-test-summary.json": ROOT / "08-10-2026/pathveiw bug checks/results/summary.json",
        KEY / "proof/03-august-10-environment.json": ROOT / "08-10-2026/pathveiw bug checks/results/environment.json",
        KEY / "proof/04-august-10-executed-notebook.ipynb": ROOT / "08-10-2026/pathveiw bug checks/pathview_deep_bug_checks.executed.ipynb",
        KEY / "proof/05-v3-status-source.json": ROOT / "08-11-2026/results/v3-audit/old-findings-status.json",
        KEY / "proof/06-v3-final-test-summary.txt": ROOT / "08-11-2026/results/pathview-plus-v3-upstream-pytest.txt",
        KEY / "proof/07-v3-final-junit.xml": ROOT / "08-11-2026/results/pathview-plus-v3-upstream-junit.xml",
        DAY / "reports/AUGUST-10-ORIGINAL-FINDINGS.md": ROOT / "08-10-2026/pathveiw bug checks/ALL-FINDINGS.md",
        DAY / "reports/V3-ORIGINAL-CHANGE-AUDIT.md": ROOT / "08-11-2026/reports/V3-CHANGE-AUDIT.md",
    }
    for destination, source in sources.items():
        if not source.exists():
            raise FileNotFoundError(source)
        copy(source, destination)


def write_manifest() -> None:
    manifest = []
    for path in sorted(DAY.rglob("*")):
        if (
            not path.is_file()
            or path.name == "manifest.csv"
            or any(part in {".mplconfig", ".ipython", "__pycache__"} for part in path.parts)
        ):
            continue
        manifest.append(
            {
                "path": str(path.relative_to(DAY)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    with (RESULTS / "manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["path", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(manifest)


def main() -> None:
    for directory in [TABLES, FIGURES, PROOF, KEY / "figures", KEY / "tables", KEY / "proof"]:
        directory.mkdir(parents=True, exist_ok=True)

    old = read_json(OLD_FINDINGS_PATH)
    old_tests = read_json(OLD_TEST_SUMMARY_PATH)
    new = read_json(NEW_STATUS_PATH)
    rows = build_rows(old, new)
    write_tables(rows)
    summary = build_summary(rows, old_tests)
    write_finding_reports(rows, summary)
    make_status_chart(summary)
    make_priority_chart(summary)
    make_visual_comparison()
    copy_key_evidence()

    for source, destination in [
        (FIGURES / "01-overall-status.png", KEY / "figures/01-overall-status.png"),
        (FIGURES / "02-priority-status.png", KEY / "figures/02-priority-status.png"),
        (FIGURES / "03-old-vs-new-half-half.png", KEY / "figures/03-old-vs-new-half-half.png"),
        (TABLES / "all-86-findings.csv", KEY / "tables/01-all-86-findings.csv"),
        (TABLES / "remaining-19.csv", KEY / "tables/02-remaining-19.csv"),
        (TABLES / "fixed-60.csv", KEY / "tables/03-fixed-60.csv"),
        (TABLES / "changed-7.csv", KEY / "tables/04-changed-7.csv"),
        (RESULTS / "comparison-summary.json", KEY / "tables/05-comparison-summary.json"),
    ]:
        copy(source, destination)
    write_manifest()
    print("Built August 12 comparison: 86 findings = 60 fixed + 19 remaining + 7 changed")


if __name__ == "__main__":
    main()
