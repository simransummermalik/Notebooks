"""Execute the small examples used by the beginner documentation.

Run from this ``pygage-sphinx`` handoff folder:

    python validation/validate_beginner_examples.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pygage import GAGEPreparation, gage  # noqa: E402
from pygage.gene_id_utils import GeneIDConverter  # noqa: E402


def check_first_analysis() -> None:
    prepared_data = pl.DataFrame(
        {
            "gene_id": [
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "11",
                "12",
            ],
            "sample_change_1": [
                2.4,
                2.0,
                1.8,
                1.5,
                -0.2,
                0.1,
                -1.8,
                -2.1,
                -1.5,
                -1.2,
                0.3,
                -0.1,
            ],
            "sample_change_2": [
                2.2,
                1.9,
                1.6,
                1.4,
                0.0,
                0.2,
                -1.7,
                -1.9,
                -1.4,
                -1.1,
                0.2,
                0.0,
            ],
        }
    )
    gene_sets = {
        "Growth pathway": ["1", "2", "3", "4"],
        "Stress pathway": ["7", "8", "9", "10"],
        "Mixed pathway": ["3", "5", "8", "11"],
    }

    result = gage(
        prepared_data,
        gene_sets,
        prepared=True,
        set_size_range=(2, 10),
    )
    significant = result.filter(pl.col("q_val") < 0.05)
    observed = set(
        significant.select("gene_set", "direction").iter_rows()
    )
    expected = {
        ("Growth pathway", "greater"),
        ("Stress pathway", "less"),
    }
    assert observed == expected, (observed, expected)


def check_raw_matrix_preparation() -> None:
    expression = pl.DataFrame(
        {
            "gene_id": ["1", "2"],
            "reference_1": [4.0, 8.0],
            "reference_2": [5.0, 7.0],
            "treatment_1": [6.0, 9.0],
            "treatment_2": [8.0, 6.0],
        }
    )
    prepared = GAGEPreparation.prepare_expression(
        expression,
        ref_indices=[0, 1],
        samp_indices=[2, 3],
        comparison="paired",
        input_logged=True,
    )
    assert prepared.columns == ["gene_id", "treatment_1", "treatment_2"]
    assert prepared["treatment_1"].to_list() == [2.0, 1.0]
    assert prepared["treatment_2"].to_list() == [3.0, -1.0]


def check_gene_id_conversion() -> None:
    converter = GeneIDConverter()
    expression = pl.DataFrame(
        {
            "gene_id": ["TP53", "BRCA1", "EGFR", "UNMATCHED"],
            "sample": [1.0, 2.0, 3.0, 4.0],
        }
    )
    conversion = converter.sym2eg(
        expression["gene_id"],
        as_frame=True,
    )
    expression_with_ids = expression.with_columns(
        pl.Series("entrez_id", conversion["output"].to_list())
    )
    expression_entrez = (
        expression_with_ids
        .filter(pl.col("entrez_id").is_not_null())
        .drop("gene_id")
        .rename({"entrez_id": "gene_id"})
    )
    assert expression_entrez["gene_id"].to_list() == [
        "7157",
        "672",
        "1956",
    ]
    assert converter.eg2sym(["7157", "672", "1956"]) == [
        "TP53",
        "BRCA1",
        "EGFR",
    ]


def main() -> None:
    check_first_analysis()
    check_raw_matrix_preparation()
    check_gene_id_conversion()
    print("Beginner examples passed.")


if __name__ == "__main__":
    main()
