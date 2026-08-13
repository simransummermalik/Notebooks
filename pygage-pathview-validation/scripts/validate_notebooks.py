#!/usr/bin/env python3
"""Fail if any delivered notebook was not fully executed or contains errors."""

from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
failed = []

for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
    nb = nbformat.read(path, as_version=4)
    code_cells = [cell for cell in nb.cells if cell.cell_type == "code"]
    unexecuted = [index for index, cell in enumerate(code_cells) if cell.get("execution_count") is None]
    errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    status = "PASS" if not unexecuted and not errors else "FAIL"
    print(f"{status}  {path.name}: {len(code_cells)} code cells, {len(errors)} error outputs")
    if unexecuted or errors:
        failed.append(path.name)

raise SystemExit(1 if failed else 0)

