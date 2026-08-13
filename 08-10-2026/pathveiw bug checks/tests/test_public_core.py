from __future__ import annotations

import compileall
import importlib
import shutil
from importlib.metadata import version
from pathlib import Path
from xml.etree import ElementTree as ET

import polars as pl
import pytest
from PIL import Image

import pathview
from pathview import PathwayResult


PUBLIC_EXPORTS = list(pathview.__all__)


def _gene_data(states: int = 1) -> pl.DataFrame:
    values: dict[str, list] = {"id": ["1029", "7157", "1956"]}
    if states >= 1:
        values["Classical"] = [-1.0, 0.0, 1.0]
    if states >= 2:
        values["Basal"] = [1.0, 0.0, -1.0]
    if states >= 3:
        values["Recovery"] = [0.0, -1.0, 1.0]
    return pl.DataFrame(values)


def _run_synthetic(
    folder: Path,
    *,
    output_format: str = "png",
    kegg_native: bool = True,
    gene_data: pl.DataFrame | None = None,
    cpd_data: pl.DataFrame | None = None,
    **kwargs,
):
    options = {
        "map_symbol": False,
        "min_nnodes": 1,
        "new_signature": False,
        "plot_col_key": False,
    }
    options.update(kwargs)
    return pathview.pathview(
        "00001",
        gene_data=_gene_data() if gene_data is None and cpd_data is None else gene_data,
        cpd_data=cpd_data,
        species="hsa",
        kegg_dir=folder,
        kegg_native=kegg_native,
        output_format=output_format,
        out_suffix=f"audit_{output_format}_{'native' if kegg_native else 'graph'}",
        **options,
    )


@pytest.mark.parametrize("export_name", PUBLIC_EXPORTS)
def test_every_declared_public_export_exists(export_name: str) -> None:
    assert hasattr(pathview, export_name), export_name
    assert getattr(pathview, export_name) is not None


def test_all_source_modules_compile() -> None:
    package_dir = Path(pathview.__file__).resolve().parent
    assert compileall.compile_dir(package_dir, quiet=1, force=True)


def test_distribution_is_importable() -> None:
    assert version("pathview-plus")
    assert callable(pathview.pathview)


@pytest.mark.xfail(
    reason="PV-BUG-001: setup.py/distribution is 2.0.2 but pathview.__version__ is 2.0.0"
)
def test_distribution_and_runtime_versions_match() -> None:
    assert version("pathview-plus") == pathview.__version__


@pytest.mark.core
def test_core_requires_at_least_one_data_table() -> None:
    with pytest.raises(ValueError, match="At least one"):
        pathview.pathview("04110", gene_data=None, cpd_data=None)


@pytest.mark.core
def test_cached_core_png_runs_without_download(
    synthetic_kegg_dir: Path, patch_hsa_species
) -> None:
    result = _run_synthetic(synthetic_kegg_dir)
    output = synthetic_kegg_dir / "hsa00001.audit_png_native.png"
    assert result and result["plot_data_gene"] is not None
    assert output.exists() and output.stat().st_size > 100
    Image.open(output).verify()


@pytest.mark.core
@pytest.mark.parametrize(
    ("kegg_native", "output_format", "renderer"),
    [
        (True, "png", "native"),
        (True, "pdf", "graph"),
        (True, "svg", "svg"),
        (False, "pdf", "graph"),
        (False, "svg", "svg"),
    ],
)
def test_documented_output_dispatch(
    synthetic_kegg_dir: Path,
    patch_hsa_species,
    monkeypatch: pytest.MonkeyPatch,
    kegg_native: bool,
    output_format: str,
    renderer: str,
) -> None:
    module = importlib.import_module("pathview.pathview")
    called: list[str] = []
    monkeypatch.setattr(module, "keggview_native", lambda **kwargs: called.append("native"))
    monkeypatch.setattr(module, "keggview_graph", lambda **kwargs: called.append("graph"))
    monkeypatch.setattr(module, "keggview_svg", lambda **kwargs: called.append("svg"))
    _run_synthetic(
        synthetic_kegg_dir,
        output_format=output_format,
        kegg_native=kegg_native,
    )
    assert called == [renderer]


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-002: --no-kegg-native with output_format='png' silently writes graph PDF"
)
def test_non_native_png_request_produces_png(
    synthetic_kegg_dir: Path, patch_hsa_species
) -> None:
    _run_synthetic(synthetic_kegg_dir, output_format="png", kegg_native=False)
    assert (synthetic_kegg_dir / "hsa00001.audit_png_graph.png").exists()


@pytest.mark.core
@pytest.mark.parametrize("bad_format", ["jpg", "PNG", "", "banana"])
@pytest.mark.xfail(
    reason="PV-BUG-003: Python API does not validate output_format; unknown values become PDF"
)
def test_python_api_rejects_unknown_output_format(
    synthetic_kegg_dir: Path,
    patch_hsa_species,
    monkeypatch: pytest.MonkeyPatch,
    bad_format: str,
) -> None:
    module = importlib.import_module("pathview.pathview")
    monkeypatch.setattr(module, "keggview_graph", lambda **kwargs: None)
    with pytest.raises(ValueError, match="output_format"):
        _run_synthetic(synthetic_kegg_dir, output_format=bad_format)


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-004: cached files cannot bypass live species lookup"
)
def test_fully_cached_human_pathway_does_not_require_network(
    synthetic_kegg_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kegg_module = importlib.import_module("pathview.kegg_api")

    def no_network(*args, **kwargs):
        raise ConnectionError("network intentionally disabled")

    monkeypatch.setattr(kegg_module.requests, "get", no_network)
    result = _run_synthetic(synthetic_kegg_dir)
    assert result


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-005: a partial color config replaces defaults instead of merging per molecule type"
)
def test_partial_color_dictionary_keeps_unspecified_defaults(
    synthetic_kegg_dir: Path, patch_hsa_species
) -> None:
    result = _run_synthetic(synthetic_kegg_dir, low={"gene": "blue"})
    assert result


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-006: map_null=False does not remove unmapped rows when a data table exists"
)
def test_map_null_false_removes_unmapped_pathway_nodes(
    synthetic_kegg_dir: Path, patch_hsa_species
) -> None:
    one_gene = pl.DataFrame({"id": ["1029"], "value": [1.0]})
    result = _run_synthetic(
        synthetic_kegg_dir,
        gene_data=one_gene,
        map_null=False,
    )
    mapped = result["plot_data_gene"]
    assert mapped.height == 1
    assert mapped["entry_id"].to_list() == ["1"]


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-007: min_nnodes counts pathway layout nodes, not nodes matched by input data"
)
def test_min_nnodes_is_based_on_input_matches(
    synthetic_kegg_dir: Path, patch_hsa_species
) -> None:
    no_match = pl.DataFrame({"id": ["99999999"], "value": [1.0]})
    result = _run_synthetic(
        synthetic_kegg_dir,
        gene_data=no_match,
        map_null=False,
        min_nnodes=1,
    )
    assert result == {}


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-008: core returns dict while documented highlighting requires PathwayResult"
)
def test_core_result_supports_documented_highlighting_interface(
    synthetic_kegg_dir: Path, patch_hsa_species
) -> None:
    result = _run_synthetic(synthetic_kegg_dir)
    assert isinstance(result, PathwayResult)
    assert result.image_array is not None


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-009: mapped core gene table omits kegg_names required by highlighting"
)
def test_core_gene_table_contains_highlighting_identifier_column(
    synthetic_kegg_dir: Path, patch_hsa_species
) -> None:
    result = _run_synthetic(synthetic_kegg_dir)
    assert "kegg_names" in result["plot_data_gene"].columns


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-075: _add_symbol_labels joins a SYMBOL column but never replaces the rendered label"
)
def test_map_symbol_updates_the_label_used_by_renderers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("pathview.pathview")
    frame = pl.DataFrame(
        {
            "entry_id": ["1"],
            "kegg_names": ["7157"],
            "label": ["7157"],
        }
    )
    monkeypatch.setattr(
        module,
        "eg2id",
        lambda ids, category, org: pl.DataFrame(
            {"ENTREZID": ["7157"], "SYMBOL": ["TP53"]}
        ),
    )
    result = module._add_symbol_labels(frame, "hsa")
    assert result["label"][0] == "TP53"


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-076: invalid node_sum ValueError is swallowed by node_map and core still returns output"
)
def test_invalid_node_sum_is_rejected_by_python_api(
    synthetic_kegg_dir: Path,
    patch_hsa_species,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("pathview.pathview")
    monkeypatch.setattr(module, "keggview_native", lambda **kwargs: None)
    with pytest.raises(ValueError, match="node_sum|sum_method"):
        _run_synthetic(synthetic_kegg_dir, node_sum="bogus")


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-010: pathway prefixes that conflict with species are concatenated, not rejected"
)
def test_conflicting_pathway_prefix_is_rejected(
    synthetic_kegg_dir: Path,
    patch_hsa_species,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("pathview.pathview")
    monkeypatch.setattr(
        module,
        "download_kegg",
        lambda *args, **kwargs: {"hsammu00001": "failed"},
    )
    with pytest.raises(ValueError, match="species|prefix"):
        pathview.pathview(
            "mmu00001",
            gene_data=_gene_data(),
            species="hsa",
            kegg_dir=synthetic_kegg_dir,
            map_symbol=False,
        )


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-011: empty KGML produces a schema-less frame and core crashes before graceful skip"
)
def test_empty_cached_pathway_is_skipped_cleanly(
    tmp_path: Path, patch_hsa_species
) -> None:
    (tmp_path / "hsa00001.xml").write_text(
        '<pathway name="path:hsa00001" number="00001"/>', encoding="utf-8"
    )
    Image.new("RGB", (50, 50), "white").save(tmp_path / "hsa00001.png")
    result = _run_synthetic(tmp_path)
    assert result == {}


@pytest.mark.core
@pytest.mark.slow
@pytest.mark.parametrize("states", [1, 2, 3])
def test_frozen_official_pathway_png_for_one_two_three_states(
    tmp_path: Path,
    frozen_hsa04110: Path,
    patch_hsa_species,
    states: int,
) -> None:
    shutil.copy2(frozen_hsa04110 / "hsa04110.xml", tmp_path / "hsa04110.xml")
    shutil.copy2(frozen_hsa04110 / "hsa04110.png", tmp_path / "hsa04110.png")
    result = pathview.pathview(
        "04110",
        gene_data=_gene_data(states),
        species="hsa",
        kegg_dir=tmp_path,
        output_format="png",
        out_suffix=f"states_{states}",
        map_symbol=False,
        min_nnodes=1,
        new_signature=False,
        plot_col_key=False,
    )
    output = tmp_path / f"hsa04110.states_{states}.png"
    assert result and output.exists() and output.stat().st_size > 10_000
    Image.open(output).verify()


@pytest.mark.core
@pytest.mark.slow
@pytest.mark.parametrize(
    ("output_format", "suffix", "magic"),
    [("svg", "svg", b"<?xml"), ("pdf", "pdf", b"%PDF")],
)
def test_frozen_official_pathway_vector_outputs(
    tmp_path: Path,
    frozen_hsa04110: Path,
    patch_hsa_species,
    output_format: str,
    suffix: str,
    magic: bytes,
) -> None:
    shutil.copy2(frozen_hsa04110 / "hsa04110.xml", tmp_path / "hsa04110.xml")
    shutil.copy2(frozen_hsa04110 / "hsa04110.png", tmp_path / "hsa04110.png")
    result = pathview.pathview(
        "04110",
        gene_data=_gene_data(2),
        species="hsa",
        kegg_dir=tmp_path,
        kegg_native=output_format != "pdf",
        output_format=output_format,
        out_suffix=f"audit_{output_format}",
        map_symbol=False,
        min_nnodes=1,
        new_signature=False,
        plot_col_key=False,
    )
    output = tmp_path / f"hsa04110.audit_{output_format}.{suffix}"
    assert result and output.read_bytes().startswith(magic)
    if output_format == "svg":
        ET.parse(output)


@pytest.mark.core
@pytest.mark.xfail(
    reason="PV-BUG-067: SVG output unnecessarily requires/downloads a KEGG PNG when kegg_native=True"
)
def test_svg_core_needs_only_cached_xml(
    tmp_path: Path,
    patch_hsa_species,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "hsa00001.xml").write_text(
        """<pathway name="path:hsa00001" number="00001">
        <entry id="1" name="hsa:1029" type="gene">
          <graphics name="CDKN2A" x="30" y="20" width="40" height="20" type="rectangle"/>
        </entry></pathway>""",
        encoding="utf-8",
    )
    module = importlib.import_module("pathview.pathview")
    requested: list[list[str]] = []

    def no_download(pathway_id, species, kegg_dir, file_type):
        requested.append(file_type)
        return {"hsa00001": "failed"}

    monkeypatch.setattr(module, "download_kegg", no_download)
    result = pathview.pathview(
        "00001",
        gene_data=pl.DataFrame({"id": ["1029"], "value": [1.0]}),
        species="hsa",
        kegg_dir=tmp_path,
        output_format="svg",
        map_symbol=False,
        min_nnodes=1,
    )
    assert requested == []
    assert result
    assert (tmp_path / "hsa00001.pathview.svg").exists()
