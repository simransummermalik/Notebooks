#!/usr/bin/env python3
"""Execute every generated notebook and save copies with embedded outputs."""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT.parent / "08-10-2026" / "notebooks"
EXECUTED = NOTEBOOKS / "executed"
EXECUTED.mkdir(parents=True, exist_ok=True)

for source in sorted(NOTEBOOKS.glob("*.ipynb")):
    notebook = nbformat.read(source, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.execute(cwd=str(ROOT))
    destination = EXECUTED / source.name
    nbformat.write(notebook, destination)
    print(f"PASS {source.name} -> {destination}")
