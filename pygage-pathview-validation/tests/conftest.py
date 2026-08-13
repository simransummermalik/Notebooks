from __future__ import annotations

import os
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"


@pytest.fixture(scope="session", autouse=True)
def _validation_environment() -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
    for folder in (
        RESULTS / "pygage",
        RESULTS / "pathview_python",
        RESULTS / "pathview_r",
        RESULTS / "comparison",
        ROOT / "cache" / "kegg",
    ):
        folder.mkdir(parents=True, exist_ok=True)

