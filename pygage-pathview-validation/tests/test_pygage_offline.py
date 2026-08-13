from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl
import pytest

import pygage
from pygage import (
    GAGEAnalysis,
    GAGEPreparation,
    GeneSetCache,
    benjamini_hochberg,
    gage,
    load_gmt,
    load_go,
    load_msigdb,
    load_reactome,
    read_de_table,
    read_matrix,
    read_preranked,
)
from pygage.config import set_thread_limits, thread_config
from pygage.data_processing_utils import DataTransformer, GeneDataExporter, GeneExtractor
from pygage.gene_sets import normalize_gene_sets
from pygage.results_analysis import ResultsComparator, SignificanceFilter, esset_grp
from pygage.visualization_utils import EnrichmentPlots, HeatmapPlotter, VennDiagram


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "results" / "pygage"
UPSTREAM_DATA = DATA / "upstream_pygage"


@pytest.fixture(scope="module")
def toy() -> tuple[pl.DataFrame, dict[str, list[str]]]:
    expression = read_matrix(DATA / "toy_expression.csv")
    sets = load_gmt(DATA / "toy_sets.gmt", source="validation", release="2026-08-10")
    return expression, sets.gene_sets


@pytest.fixture(scope="module")
def prepared(toy) -> tuple[pl.DataFrame, dict[str, list[str]]]:
    expression, sets = toy
    frame = GAGEPreparation.prepare_expression(
        expression,
        ref_indices=[0, 1],
        samp_indices=[2, 3],
        comparison="paired",
    )
    return frame, sets


def test_import_and_version() -> None:
    assert pygage.__version__ == "1.2.1"
    assert callable(gage)


def test_benjamini_hochberg_known_values() -> None:
    got = benjamini_hochberg(np.array([0.01, 0.04, 0.03, np.nan]))
    np.testing.assert_allclose(got[:3], [0.03, 0.04, 0.04])
    assert np.isnan(got[3])


@pytest.mark.parametrize("comparison,width", [
    ("paired", 3),
    ("unpaired", 5),
    ("as.group", 2),
    ("1ongroup", 3),
])
def test_all_documented_preparation_modes(toy, comparison: str, width: int) -> None:
    expression, _ = toy
    got = GAGEPreparation.prepare_expression(
        expression,
        ref_indices=[0, 1],
        samp_indices=[2, 3],
        comparison=comparison,
    )
    assert got.width == width
    assert got.height == expression.height
    assert got.columns[0] == "gene_id"


def test_unsigned_and_raw_count_preparation(toy) -> None:
    expression, _ = toy
    signed = GAGEPreparation.prepare_expression(
        expression, [0, 1], [2, 3], comparison="paired", same_dir=True
    )
    unsigned = GAGEPreparation.prepare_expression(
        expression, [0, 1], [2, 3], comparison="paired", same_dir=False
    )
    assert np.all(unsigned.drop("gene_id").to_numpy() >= 0)
    np.testing.assert_allclose(
        unsigned.drop("gene_id").to_numpy(),
        np.abs(signed.drop("gene_id").to_numpy()),
    )

    counts = pl.DataFrame({"gene_id": ["a", "b"], "c": [3, 7], "t": [7, 15]})
    logged = GAGEPreparation.prepare_expression(
        counts, [0], [1], input_logged=False
    )
    np.testing.assert_allclose(logged["t"].to_numpy(), [1.0, 1.0])


@pytest.mark.parametrize("test_method", ["t-test", "z-test", "ks-test"])
@pytest.mark.parametrize("meta_method", ["stouffer", "fisher"])
def test_statistical_and_meta_methods(prepared, test_method: str, meta_method: str) -> None:
    frame, sets = prepared
    result = GAGEAnalysis().run_gage(
        frame,
        sets,
        set_size_range=(5, 50),
        test_method=test_method,
        meta_method=meta_method,
    )
    assert set(result) == {"greater", "less", "stats"}
    assert result["greater"].height == len(sets)
    assert result["less"].height == len(sets)
    assert result["greater"]["p_val"].is_between(0, 1, closed="both").all()


def test_extended_analysis_options_are_deterministic(prepared) -> None:
    frame, sets = prepared
    kwargs = dict(
        set_size_range=(5, 50),
        control_genes=[f"g{i:02d}" for i in range(21, 31)],
        global_bh=True,
        compute_effect=True,
        leading_edge=True,
        permutations=8,
        random_state=42,
        n_jobs=2,
    )
    first_engine = GAGEAnalysis()
    first = first_engine.run_gage(frame, sets, **kwargs)
    second = GAGEAnalysis().run_gage(frame, sets, **kwargs)
    assert {"effect", "leading_edge", "p_perm"}.issubset(first["greater"].columns)
    np.testing.assert_allclose(first["greater"]["p_perm"], second["greater"]["p_perm"])
    assert first_engine.result_obj is not None
    assert first_engine.result_obj.meta["test_method"] == "t-test"
    assert first_engine.result_obj.meta["n_samples"] == 2


def test_directionless_analysis(prepared) -> None:
    frame, sets = prepared
    result = GAGEAnalysis().run_gage(
        frame,
        sets,
        set_size_range=(5, 50),
        same_dir=False,
    )
    assert "less" not in result
    assert set(result) == {"greater", "stats"}


def test_convenience_gage_raw_and_prepared(toy, prepared) -> None:
    expression, sets = toy
    prepared_frame, _ = prepared
    raw_tidy = gage(
        expression,
        sets,
        ref_indices=[0, 1],
        samp_indices=[2, 3],
        set_size_range=(5, 50),
    )
    prepared_tidy = gage(
        prepared_frame,
        sets,
        prepared=True,
        set_size_range=(5, 50),
    )
    assert set(raw_tidy["direction"]) == {"greater", "less"}
    assert raw_tidy.shape == prepared_tidy.shape


def test_input_adapters_accept_files_frames_pandas_and_dict(tmp_path: Path) -> None:
    matrix = read_matrix(DATA / "toy_expression.csv")
    assert matrix["gene_id"].dtype == pl.String

    pandas_matrix = pd.DataFrame({"gene_id": ["a", "b"], "s1": [1.0, 2.0]})
    assert read_matrix(pandas_matrix).shape == (2, 2)
    assert read_matrix({"gene_id": ["a"], "s1": [1.0]}).shape == (1, 2)

    de_path = tmp_path / "deseq2.csv"
    pl.DataFrame({
        "gene": ["a", "b"],
        "log2FoldChange": [1.5, -2.0],
        "stat": [3.0, -4.0],
    }).write_csv(de_path)
    de_lfc = read_de_table(de_path)
    de_stat = read_de_table(de_path, value="stat")
    assert de_lfc.columns == ["gene_id", "log2FC"]
    assert de_stat.columns == ["gene_id", "stat"]
    assert read_preranked({"a": 2.0, "b": -1.0}).shape == (2, 2)


def test_anndata_input_adapter() -> None:
    import anndata as ad

    adata = ad.AnnData(
        X=np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
        obs=pd.DataFrame(index=["sample_1", "sample_2"]),
        var=pd.DataFrame(index=["g1", "g2", "g3"]),
    )
    got = read_matrix(adata)
    assert got.shape == (3, 3)
    assert got.columns == ["gene_id", "sample_1", "sample_2"]
    assert got["gene_id"].to_list() == ["g1", "g2", "g3"]


def test_gene_set_formats_go_propagation_and_cache(tmp_path: Path) -> None:
    gmt = load_gmt(DATA / "toy_sets.gmt", source="GMT", release="test")
    msigdb = load_msigdb(DATA / "toy_sets.gmt", collection="H")
    reactome_gmt = load_reactome(DATA / "toy_sets.gmt")
    assert gmt.n_sets == msigdb.n_sets == reactome_gmt.n_sets == 4
    assert msigdb.source == "MSigDB"
    assert reactome_gmt.source == "Reactome"
    assert normalize_gene_sets(gmt)["UP_SET"][0] == "g01"

    go = load_go(
        DATA / "toy_annotations.gaf",
        obo_path=DATA / "toy_go.obo",
        aspect="BP",
        include_iea=True,
        propagate=True,
    )
    assert "G01" in go.gene_sets["GO:0000001"]
    assert "G02" in go.gene_sets["GO:0000001"]

    cache = GeneSetCache(tmp_path / "cache")
    saved = cache.save("toy/v1", gmt)
    restored = cache.load("toy/v1")
    assert saved.exists()
    assert cache.list_keys() == ["toy_v1"]
    assert restored is not None and restored.gene_sets == gmt.gene_sets
    assert restored.checksum == gmt.checksum


def test_transform_extract_export_and_result_helpers(toy, prepared, tmp_path: Path) -> None:
    expression, sets = toy
    frame, _ = prepared
    row = DataTransformer.row_normalize(expression)
    col = DataTransformer.column_normalize(expression)
    np.testing.assert_allclose(row.drop("gene_id").to_numpy().mean(axis=1), 0, atol=1e-12)
    np.testing.assert_allclose(col.drop("gene_id").to_numpy().mean(axis=0), 0, atol=1e-12)

    extracted = GeneExtractor.extract_essential_genes(sets["UP_SET"], frame, threshold=0.1)
    assert extracted.height > 0
    export = tmp_path / "genes.csv"
    heatmap = tmp_path / "genes.png"
    GeneDataExporter.export_gene_data(
        sets["UP_SET"], frame, output_file=export, create_heatmap=True, heatmap_output=heatmap
    )
    assert export.exists() and heatmap.exists()

    analysis = GAGEAnalysis()
    result = analysis.run_gage(frame, sets, set_size_range=(5, 50))
    filtered = SignificanceFilter.filter_significant(result, cutoff=1.0)
    assert filtered["greater"].height == result["greater"].height
    grouped = esset_grp(
        result["greater"], frame, sets, cutoff=1.0, pc=1.0
    )
    assert "groups" in grouped and "core_genes" in grouped


def test_comparison_and_all_plot_families(prepared, tmp_path: Path) -> None:
    frame, sets = prepared
    result = GAGEAnalysis().run_gage(frame, sets, set_size_range=(5, 50))
    greater = result["greater"]
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    greater.write_csv(first)
    greater.with_columns((pl.col("q_val") * 0.9).alias("q_val")).write_csv(second)
    comparison = ResultsComparator.compare_results(
        [first, second], ["A", "B"], q_cutoff=1.0, output_file=tmp_path / "compared.csv"
    )
    assert "hits" in comparison.columns

    counts = VennDiagram.venn_counts(pl.DataFrame({"A": [1, 1, 0], "B": [1, 0, 1]}))
    VennDiagram.plot_venn2(counts, ["A", "B"], tmp_path / "venn.png")
    HeatmapPlotter.plot_heatmap(
        frame.drop("gene_id").head(10),
        row_labels=frame["gene_id"].head(10).to_list(),
        output_file=tmp_path / "heatmap.png",
    )
    HeatmapPlotter.plot_clustered_heatmap(
        frame.head(10), output_file=tmp_path / "clustered.png"
    )
    EnrichmentPlots.bubble_plot(greater, output_file=tmp_path / "bubble.png")
    EnrichmentPlots.enrichment_heatmap(
        {"A": greater, "B": greater}, output_file=tmp_path / "enrichment_heatmap.png"
    )
    ranked = frame.select(
        "gene_id", pl.mean_horizontal(pl.exclude("gene_id")).alias("score")
    )
    running = EnrichmentPlots.running_enrichment(
        ranked, sets["UP_SET"], output_file=tmp_path / "running.png"
    )
    assert running["n_hits"] == 10
    assert all((tmp_path / name).exists() for name in [
        "venn.png", "heatmap.png", "clustered.png", "bubble.png",
        "enrichment_heatmap.png", "running.png",
    ])


@pytest.mark.xfail(reason="Matplotlib 3.11 removed matplotlib.cm.get_cmap used by this new PyGAGE chart")
def test_new_pathway_gene_color_chart(prepared, tmp_path: Path) -> None:
    frame, sets = prepared
    ranked = frame.select(
        "gene_id", pl.mean_horizontal(pl.exclude("gene_id")).alias("score")
    )
    colors = EnrichmentPlots.pathway_gene_colors(
        sets["UP_SET"],
        dict(zip(ranked["gene_id"], ranked["score"])),
        output_file=tmp_path / "pathway_colors.png",
    )
    assert len(colors) == 10
    assert (tmp_path / "pathway_colors.png").exists()


def test_thread_configuration() -> None:
    import os

    set_thread_limits(2)
    cfg = thread_config()
    assert cfg["OMP_NUM_THREADS"] == "2"
    assert os.environ["OPENBLAS_NUM_THREADS"] == "2"


@pytest.mark.xfail(reason="pygage.__all__ names normalize_gene_sets without importing it at package scope")
def test_star_import_contract() -> None:
    namespace: dict[str, object] = {}
    exec("from pygage import *", namespace)
    assert callable(namespace["normalize_gene_sets"])


@pytest.mark.xfail(reason="Documented repeated paired design does not repeat reference columns before subtraction")
def test_multiple_sample_blocks_per_reference_are_supported() -> None:
    frame = pl.DataFrame({
        "gene_id": ["g1", "g2"],
        "r1": [1.0, 2.0],
        "r2": [1.5, 2.5],
        "s1": [2.0, 3.0],
        "s2": [2.5, 3.5],
        "s3": [3.0, 4.0],
        "s4": [3.5, 4.5],
    })
    got = GAGEPreparation.prepare_expression(
        frame,
        ref_indices=[0, 1],
        samp_indices=[2, 3, 4, 5],
        comparison="paired",
    )
    assert got.shape == (2, 5)


@pytest.mark.xfail(reason="Permutation shuffles prepared columns, leaving the cross-column statistic invariant")
def test_permutation_null_is_informative(prepared) -> None:
    frame, sets = prepared
    result = GAGEAnalysis().run_gage(
        frame,
        sets,
        set_size_range=(5, 50),
        permutations=20,
        random_state=7,
    )
    assert result["greater"]["p_perm"].n_unique() > 1
    assert not np.allclose(result["greater"]["p_perm"], 1.0)


@pytest.mark.parametrize("method,meta,reference_name", [
    ("t-test", "stouffer", "gage_tTest_greater.csv.gz"),
    ("z-test", "stouffer", "gage_zTest_greater.csv.gz"),
    ("t-test", "fisher", "gage_fisher_greater.csv.gz"),
])
def test_packaged_r_gage_regression_parity(method: str, meta: str, reference_name: str) -> None:
    regression = UPSTREAM_DATA
    prepared = pl.read_csv(
        regression / "gse16873_prepared.csv.gz",
        schema_overrides={"gene_id": pl.String},
    )
    sets = json.loads((regression / "kegg_gs.json").read_text())
    got = GAGEAnalysis().run_gage(
        prepared,
        sets,
        test_method=method,
        meta_method=meta,
        compute_effect=False,
    )["greater"]
    expected = pl.read_csv(
        regression / reference_name,
        null_values="NA",
        infer_schema_length=None,
    ).select(
        "gene_set",
        pl.col("stat.mean").alias("expected_stat"),
        pl.col("p.val").alias("expected_p"),
    )
    joined = got.join(expected, on="gene_set", how="inner")
    assert joined.height == got.height
    np.testing.assert_allclose(joined["stat_mean"], joined["expected_stat"], rtol=2e-13, atol=2e-13)
    np.testing.assert_allclose(joined["p_val"], joined["expected_p"], rtol=2e-12, atol=1e-250)


def test_new_gds3627_file_is_readable_and_design_is_identifiable() -> None:
    frame = read_matrix(UPSTREAM_DATA / "GDS3627_exp_formatted.csv")
    assert frame.shape == (19469, 199)
    assert frame["gene_id"].dtype == pl.String
    tumor = [c for c in frame.columns[1:] if c.endswith(".01")]
    normal = [c for c in frame.columns[1:] if c.endswith(".11")]
    assert len(tumor) > 0 and len(normal) > 0
    assert len(tumor) == 184 and len(normal) == 13
    assert len(tumor) + len(normal) == 197
    unmatched = set(frame.columns[1:]) - set(tumor) - set(normal)
    assert len(unmatched) == 1
