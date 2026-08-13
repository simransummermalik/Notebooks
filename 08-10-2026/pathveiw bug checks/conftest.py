from __future__ import annotations

import importlib
import os
from pathlib import Path

import numpy as np
import polars as pl
import pytest
from PIL import Image


AUDIT_ROOT = Path(__file__).resolve().parent
WORKSPACE = AUDIT_ROOT.parent
VALIDATION_ROOT = WORKSPACE / "pygage-pathview-validation"


@pytest.fixture
def simple_node_data() -> pl.DataFrame:
    """Three controlled KGML-style nodes: two genes and one compound."""
    return pl.DataFrame(
        {
            "entry_id": ["1", "2", "3"],
            "name": ["hsa:1029", "hsa:7157 hsa:1956", "cpd:C00031"],
            "type": ["gene", "gene", "compound"],
            "x": [30.0, 80.0, 55.0],
            "y": [20.0, 60.0, 20.0],
            "width": [40.0, 40.0, 10.0],
            "height": [20.0, 20.0, 10.0],
            "bgcolor": ["#FFFFFF", "#FFFFFF", "#FFFFFF"],
            "label": ["CDKN2A", "TP53, EGFR", "Glucose"],
            "shape": ["rectangle", "rectangle", "circle"],
            "reaction": ["", "", "rn:R1"],
            "component": ["", "", ""],
            "size": [1, 1, 1],
        }
    )


@pytest.fixture
def simple_gene_plot() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "entry_id": ["1", "2"],
            "name": ["hsa:1029", "hsa:7157"],
            "type": ["gene", "gene"],
            "x": [30.0, 80.0],
            "y": [20.0, 60.0],
            "width": [40.0, 40.0],
            "height": [20.0, 20.0],
            "bgcolor": ["#FFFFFF", "#FFFFFF"],
            "label": ["CDKN2A", "TP53"],
            "shape": ["rectangle", "rectangle"],
            "reaction": ["", ""],
            "component": ["", ""],
            "size": [1, 1],
            "kegg_names": ["1029", "7157"],
            "A": [-1.0, 1.0],
            "B": [1.0, -1.0],
        }
    )


@pytest.fixture
def simple_compound_plot() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "entry_id": ["3"],
            "name": ["cpd:C00031"],
            "type": ["compound"],
            "x": [55.0],
            "y": [20.0],
            "width": [10.0],
            "height": [10.0],
            "bgcolor": ["#FFFFFF"],
            "label": ["Glucose"],
            "shape": ["circle"],
            "reaction": ["rn:R1"],
            "component": [""],
            "size": [1],
            "kegg_names": ["C00031"],
            "A": [1.0],
            "B": [-1.0],
        }
    )


@pytest.fixture
def synthetic_kegg_dir(tmp_path: Path) -> Path:
    """A complete tiny cached pathway, so the core can run without a network."""
    xml = """<?xml version="1.0"?>
<pathway name="path:hsa00001" number="00001" title="Controlled pathway">
  <entry id="1" name="hsa:1029" type="gene">
    <graphics name="CDKN2A" x="30" y="20" width="40" height="20" type="rectangle" bgcolor="#FFFFFF"/>
  </entry>
  <entry id="2" name="hsa:7157 hsa:1956" type="gene">
    <graphics name="TP53, EGFR" x="80" y="60" width="40" height="20" type="rectangle" bgcolor="#FFFFFF"/>
  </entry>
  <entry id="3" name="cpd:C00031" type="compound" reaction="rn:R1">
    <graphics name="Glucose" x="55" y="20" width="10" height="10" type="circle" bgcolor="#FFFFFF"/>
  </entry>
  <relation entry1="1" entry2="2" type="PPrel">
    <subtype name="activation" value="--&gt;"/>
  </relation>
  <reaction name="rn:R1" type="irreversible">
    <substrate id="3"/><product id="1"/>
  </reaction>
</pathway>
"""
    (tmp_path / "hsa00001.xml").write_text(xml, encoding="utf-8")
    Image.fromarray(np.full((100, 120, 3), 255, dtype=np.uint8)).save(
        tmp_path / "hsa00001.png"
    )
    return tmp_path


@pytest.fixture
def patch_hsa_species(monkeypatch: pytest.MonkeyPatch):
    """Patch only species discovery; cached files and all later code remain real."""
    from pathview import SpeciesInfo

    module = importlib.import_module("pathview.pathview")
    info = SpeciesInfo("hsa", True, None, None, None, None)
    monkeypatch.setattr(module, "kegg_species_code", lambda species="hsa": info)
    return info


@pytest.fixture
def frozen_hsa04110() -> Path:
    candidates = [
        VALIDATION_ROOT / "cache" / "kegg",
        VALIDATION_ROOT / ".r-library" / "pathview" / "extdata",
    ]
    for folder in candidates:
        if (folder / "hsa04110.xml").exists() and (folder / "hsa04110.png").exists():
            return folder
    pytest.skip("Frozen official hsa04110 KGML/PNG fixture is not available")


class FakeResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        text: str = "",
        content: bytes | None = None,
        json_data=None,
        headers: dict | None = None,
    ):
        self.status_code = status_code
        self.text = text
        self.content = content if content is not None else text.encode()
        self._json_data = json_data
        self.headers = headers or {}

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    def raise_for_status(self) -> None:
        if not self.ok:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        if self._json_data is None:
            raise ValueError("not JSON")
        return self._json_data


@pytest.fixture(autouse=True)
def stable_matplotlib_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("MPLBACKEND", "Agg")
    monkeypatch.setenv("MPLCONFIGDIR", os.fspath(tmp_path / "mpl"))

