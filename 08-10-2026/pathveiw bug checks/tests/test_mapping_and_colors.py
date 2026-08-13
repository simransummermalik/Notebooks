from __future__ import annotations

import numpy as np
import polars as pl
import pytest
import subprocess
import sys

from pathview import make_colormap, mol_sum, node_color, node_map, sim_mol_data
from pathview.utils import max_abs, random_pick


@pytest.mark.mapping
@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("sum", 2.0),
        ("mean", 1.0),
        ("median", 1.0),
        ("max", 3.0),
    ],
)
def test_supported_molecule_aggregations(method: str, expected: float) -> None:
    data = pl.DataFrame({"probe": ["a", "b"], "value": [-1.0, 3.0]})
    mapping = pl.DataFrame({"probe": ["a", "b"], "entrez": ["1", "1"]})
    result = mol_sum(data, mapping, sum_method=method)
    assert result.shape == (1, 2)
    assert result["value"][0] == expected


@pytest.mark.mapping
def test_unknown_aggregation_is_rejected() -> None:
    data = pl.DataFrame({"probe": ["a"], "value": [1.0]})
    mapping = pl.DataFrame({"probe": ["a"], "entrez": ["1"]})
    with pytest.raises(ValueError, match="Unknown sum_method"):
        mol_sum(data, mapping, sum_method="not-a-method")


@pytest.mark.mapping
@pytest.mark.parametrize("method", ["max_abs", "random"])
@pytest.mark.xfail(
    reason="PV-BUG-012: group aggregation UDF receives scalar elements under current Polars"
)
def test_all_advertised_aggregations_work(method: str) -> None:
    data = pl.DataFrame({"probe": ["a", "b"], "value": [-1.0, 3.0]})
    mapping = pl.DataFrame({"probe": ["a", "b"], "entrez": ["1", "1"]})
    result = mol_sum(data, mapping, sum_method=method)
    assert result.height == 1
    assert result["value"][0] in {-1.0, 3.0}
    if method == "max_abs":
        assert result["value"][0] == 3.0


@pytest.mark.mapping
def test_no_matching_ids_has_clear_error() -> None:
    data = pl.DataFrame({"probe": ["a"], "value": [1.0]})
    mapping = pl.DataFrame({"probe": ["b"], "entrez": ["1"]})
    with pytest.raises(ValueError, match="No IDs"):
        mol_sum(data, mapping)


@pytest.mark.mapping
@pytest.mark.xfail(
    reason="PV-BUG-013: mol_sum casts data IDs to strings but not mapping IDs"
)
def test_mol_sum_normalizes_both_id_column_types() -> None:
    data = pl.DataFrame({"probe": [1, 2], "value": [1.0, 2.0]})
    mapping = pl.DataFrame({"probe": [1, 2], "entrez": ["10", "20"]})
    result = mol_sum(data, mapping)
    assert result["probe"].to_list() == ["10", "20"]


@pytest.mark.mapping
@pytest.mark.xfail(
    reason="PV-BUG-014: null mapping targets are aggregated into a null output ID"
)
def test_null_mapping_targets_are_removed() -> None:
    data = pl.DataFrame({"probe": ["a", "b"], "value": [1.0, 2.0]})
    mapping = pl.DataFrame({"probe": ["a", "b"], "entrez": ["10", None]})
    result = mol_sum(data, mapping)
    assert result["probe"].null_count() == 0
    assert result.height == 1


@pytest.mark.mapping
@pytest.mark.xfail(
    reason="PV-BUG-015: duplicated mapping pairs duplicate the input value before aggregation"
)
def test_duplicate_mapping_pairs_do_not_double_count() -> None:
    data = pl.DataFrame({"probe": ["a"], "value": [2.0]})
    mapping = pl.DataFrame({"probe": ["a", "a"], "entrez": ["10", "10"]})
    result = mol_sum(data, mapping)
    assert result["value"][0] == 2.0


@pytest.mark.mapping
def test_one_source_can_map_to_two_targets() -> None:
    data = pl.DataFrame({"probe": ["a"], "value": [2.0]})
    mapping = pl.DataFrame({"probe": ["a", "a"], "entrez": ["10", "20"]})
    result = mol_sum(data, mapping).sort("probe")
    assert result["probe"].to_list() == ["10", "20"]
    assert result["value"].to_list() == [2.0, 2.0]


@pytest.mark.mapping
def test_multi_id_pathway_node_aggregates_all_matching_genes(simple_node_data) -> None:
    genes = pl.DataFrame({"id": ["7157", "1956"], "value": [1.5, 2.5]})
    result = node_map(genes, simple_node_data, node_types="gene", node_sum="sum")
    row = result.filter(pl.col("entry_id") == "2")
    assert row["value"][0] == 4.0


@pytest.mark.mapping
def test_layout_only_node_map_has_identifier_and_nan(simple_node_data) -> None:
    result = node_map(None, simple_node_data, node_types="gene")
    assert result.height == 2
    assert {"entry_id", "kegg_names", "mol_val"}.issubset(result.columns)
    assert result["mol_val"].is_nan().all()


@pytest.mark.mapping
def test_missing_requested_node_type_returns_none(simple_node_data) -> None:
    assert node_map(None, simple_node_data, node_types="ortholog") is None


@pytest.mark.mapping
@pytest.mark.xfail(
    reason="PV-BUG-009: mapped node table drops the exploded kegg_names identifier"
)
def test_mapped_node_table_retains_kegg_names(simple_node_data) -> None:
    genes = pl.DataFrame({"id": ["1029"], "value": [1.0]})
    result = node_map(genes, simple_node_data, node_types="gene")
    assert "kegg_names" in result.columns
    assert result.filter(pl.col("entry_id") == "1")["kegg_names"][0] == "1029"


@pytest.mark.mapping
@pytest.mark.xfail(
    reason="PV-BUG-016: entrez_gnodes is unused and species prefixes are always stripped"
)
def test_kegg_gene_ids_can_be_mapped_without_stripping_prefix(simple_node_data) -> None:
    genes = pl.DataFrame({"id": ["hsa:1029"], "value": [1.0]})
    result = node_map(
        genes,
        simple_node_data,
        node_types="gene",
        entrez_gnodes=False,
    )
    assert result is not None
    assert result.filter(pl.col("entry_id") == "1")["value"][0] == 1.0


@pytest.mark.mapping
def test_simulated_compounds_are_seeded_and_unique() -> None:
    first = sim_mol_data("cpd", n_mol=25, n_exp=3, rand_seed=7)
    second = sim_mol_data("cpd", n_mol=25, n_exp=3, rand_seed=7)
    assert first.equals(second)
    assert first.shape == (25, 4)
    assert first["id"].n_unique() == 25


@pytest.mark.mapping
def test_simulated_discrete_compounds_have_only_ids() -> None:
    result = sim_mol_data("cpd", n_mol=5, n_exp=9, rand_seed=1, discrete=True)
    assert result.columns == ["id"]
    assert result.height == 5


@pytest.mark.mapping
@pytest.mark.xfail(reason="PV-BUG-017: negative experiment count is silently accepted")
def test_simulation_rejects_negative_experiment_count() -> None:
    with pytest.raises(ValueError, match="n_exp"):
        sim_mol_data("cpd", n_mol=5, n_exp=-1)


@pytest.mark.mapping
def test_low_level_custom_aggregators_handle_nan() -> None:
    values = np.array([np.nan, -2.0, 1.0])
    assert max_abs(values) == -2.0
    assert random_pick(np.array([np.nan, 4.0])) == 4.0
    assert np.isnan(max_abs(np.array([np.nan])))


@pytest.mark.color
def test_continuous_color_mapping_clips_and_handles_missing_values() -> None:
    frame = pl.DataFrame(
        {"id": ["lo", "zero", "hi", "missing"], "v": [-2.0, 0.0, 2.0, None]}
    )
    result = node_color(
        frame,
        limit=1.0,
        bins=11,
        low="#00FF00",
        mid="#BEBEBE",
        high="#FF0000",
        na_col="transparent",
    )
    assert result["v_col"].to_list() == [
        "#00FF00",
        "#BEBEBE",
        "#FF0000",
        "transparent",
    ]


@pytest.mark.color
def test_asymmetric_tuple_limits_and_one_direction() -> None:
    frame = pl.DataFrame({"id": ["a", "b", "c"], "v": [-5.0, 1.0, 3.0]})
    asymmetric = node_color(
        frame, limit=(-5.0, 3.0), bins=9, low="blue", mid="white", high="red"
    )
    one_direction = node_color(
        frame, limit=3.0, both_dirs=False, bins=9, low="blue", mid="white", high="red"
    )
    assert asymmetric["v_col"][0] == "#0000FF"
    assert asymmetric["v_col"][2] == "#FF0000"
    assert one_direction["v_col"][0] == "#0000FF"
    assert one_direction["v_col"][2] == "#FF0000"


@pytest.mark.color
def test_color_transform_is_applied_before_mapping() -> None:
    frame = pl.DataFrame({"id": ["a", "b"], "v": [-2.0, 2.0]})
    result = node_color(frame, limit=2.0, bins=11, trans_fun=np.abs)
    assert result["v_col"][0] == result["v_col"][1]


@pytest.mark.color
def test_infinities_are_clipped_to_endpoints() -> None:
    frame = pl.DataFrame({"id": ["a", "b"], "v": [-np.inf, np.inf]})
    result = node_color(
        frame, limit=1.0, bins=11, low="#0000FF", mid="#FFFFFF", high="#FF0000"
    )
    assert result["v_col"].to_list() == ["#0000FF", "#FF0000"]


@pytest.mark.color
def test_each_value_column_gets_one_color_column() -> None:
    frame = pl.DataFrame({"id": ["a"], "A": [-1.0], "B": [0.0], "C": [1.0]})
    result = node_color(frame, bins=11)
    assert result.columns == ["id", "A_col", "B_col", "C_col"]


@pytest.mark.color
@pytest.mark.xfail(
    reason="PV-BUG-018: decimal strings are parsed as hexadecimal numbers"
)
def test_decimal_string_values_mean_the_same_as_decimal_numbers() -> None:
    strings = node_color(pl.DataFrame({"id": ["x"], "v": ["10"]}), limit=20, bins=41)
    numbers = node_color(pl.DataFrame({"id": ["x"], "v": [10.0]}), limit=20, bins=41)
    assert strings["v_col"][0] == numbers["v_col"][0]


@pytest.mark.color
@pytest.mark.xfail(
    reason="PV-FEATURE-001: discrete is accepted by public APIs but ignored by node_color"
)
def test_discrete_setting_changes_color_mapping_mode() -> None:
    frame = pl.DataFrame({"id": ["a", "b", "c"], "v": [0.0, 1.0, 2.0]})
    continuous = node_color(frame, limit=(0, 2), bins=11, discrete=False)
    discrete = node_color(frame, limit=(0, 2), bins=11, discrete=True)
    assert not continuous.equals(discrete)


@pytest.mark.color
@pytest.mark.parametrize("bad_bins", [0, -1])
def test_nonpositive_color_bin_counts_are_rejected(bad_bins: int) -> None:
    with pytest.raises(ValueError):
        node_color(pl.DataFrame({"id": ["x"], "v": [1.0]}), bins=bad_bins)


@pytest.mark.color
def test_colormap_accepts_named_and_hex_colors() -> None:
    assert make_colormap("blue", "#FFFFFF", "red", n=17).N == 17


@pytest.mark.mapping
@pytest.mark.xfail(
    reason="PV-BUG-079: wordwrap width=0 with break_word=True makes no progress and loops forever"
)
def test_hard_wordwrap_rejects_zero_width_instead_of_hanging() -> None:
    code = (
        "from pathview import wordwrap; "
        "wordwrap('this cannot advance', width=0, break_word=True)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        text=True,
        capture_output=True,
        timeout=2,
        check=False,
    )
    assert result.returncode != 0
    assert "width" in result.stderr.lower()
