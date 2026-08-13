#!/usr/bin/env python3
"""Run the complete local validation workflow in the correct order."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], env: dict[str, str]) -> None:
    print("\nRUN:", " ".join(command))
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="also run fresh KEGG service/pathway checks")
    parser.add_argument(
        "--execute-notebooks",
        action="store_true",
        help="rerun and overwrite the four notebooks with fresh outputs",
    )
    args = parser.parse_args(argv)

    python = sys.executable
    env = os.environ.copy()
    env.setdefault("MPLBACKEND", "Agg")
    env.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
    env["R_LIBS_USER"] = str(ROOT / ".r-library")

    run([
        python, "-m", "pytest", "-q",
        "tests/test_pygage_offline.py", "tests/test_pathview_offline.py",
        "--junitxml=reports/offline-junit.xml",
    ], env)
    run([python, "scripts/run_pygage_validation.py"], env)
    pathview_command = [python, "scripts/run_pathview_validation.py"]
    if args.live:
        pathview_command.append("--live")
    run(pathview_command, env)
    run(["Rscript", "scripts/run_r_pathview.R"], env)
    run([python, "scripts/compare_r_python.py"], env)

    if args.execute_notebooks:
        for notebook in sorted((ROOT / "notebooks").glob("*.ipynb")):
            run([
                str(ROOT / ".venv" / "bin" / "jupyter"),
                "nbconvert", "--to", "notebook", "--execute", "--inplace",
                "--ExecutePreprocessor.timeout=600", str(notebook),
            ], env)

    run([python, "scripts/validate_notebooks.py"], env)
    run([python, "scripts/build_report.py"], env)
    print("\nComplete. Open notebooks/00_START_HERE.ipynb.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

