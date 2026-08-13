#!/usr/bin/env python3
"""Execute the reproducible PyGAGE demonstrations and save evidence."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import polars as pl

from pygage import GAGEAnalysis, GAGEPreparation, gage, load_gmt, read_matrix
from pygage.visualization_utils import EnrichmentPlots


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "results" / "pygage"
UPSTREAM_DATA = DATA / "upstream_pygage"
OUT.mkdir(parents=True, exist_ok=True)

REPORT: dict[str, object] = {
    "component": "PyGAGE",
    "repository_commit": "265ab1a07a3987eba41779931053fbe7b3ef4fd3",
    "version": "1.2.1",
    "python": platform.python_version(),
    "checks": [],
}


def check(name: str, fn) -> object | None:
    started = time.perf_counter()
    try:
        details = fn()
        REPORT["checks"].append({
            "name": name,
            "status": "pass",
            "seconds": round(time.perf_counter() - started, 4),
            "details": details,
        })
        print(f"PASS  {name}")
        return details
    except Exception as exc:
        REPORT["checks"].append({
            "name": name,
            "status": "fail",
            "seconds": round(time.perf_counter() - started, 4),
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        })
        print(f"FAIL  {name}: {exc}")
        return None


def toy_analysis() -> dict[str, object]:
    expression = read_matrix(DATA / "toy_expression.csv")
    collection = load_gmt(DATA / "toy_sets.gmt", source="validation", release="2026-08-10")
    prepared = GAGEPreparation.prepare_expression(
        expression,
        ref_indices=[0, 1],
        samp_indices=[2, 3],
        comparison="paired",
    )
    prepared.write_csv(OUT / "toy_prepared.csv")

    result = GAGEAnalysis().run_gage(
        prepared,
        collection,
        set_size_range=(5, 50),
        compute_effect=True,
        leading_edge=True,
    )
    result["greater"].write_csv(OUT / "toy_greater.csv")
    result["less"].write_csv(OUT / "toy_less.csv")

    up_top = result["greater"].sort("p_val")["gene_set"][0]
    down_top = result["less"].sort("p_val")["gene_set"][0]
    if up_top != "UP_SET" or down_top != "DOWN_SET":
        raise AssertionError(f"unexpected toy ranking: greater={up_top}, less={down_top}")

    EnrichmentPlots.bubble_plot(
        result["greater"],
        top_n=4,
        title="Toy PyGAGE enrichment",
        output_file=OUT / "toy_bubble.png",
    )
    ranked = prepared.select(
        "gene_id", pl.mean_horizontal(pl.exclude("gene_id")).alias("score")
    )
    running = EnrichmentPlots.running_enrichment(
        ranked,
        collection.gene_sets["UP_SET"],
        title="UP_SET running enrichment",
        output_file=OUT / "toy_running_enrichment.png",
    )
    return {
        "input_shape": list(expression.shape),
        "prepared_shape": list(prepared.shape),
        "gene_sets": collection.n_sets,
        "top_greater": up_top,
        "top_less": down_top,
        "running_ES": running["ES"],
    }


def statistic_matrix() -> dict[str, object]:
    expression = read_matrix(DATA / "toy_expression.csv")
    sets = load_gmt(DATA / "toy_sets.gmt").gene_sets
    prepared = GAGEPreparation.prepare_expression(expression, [0, 1], [2, 3])
    rows = []
    for method in ("t-test", "z-test", "ks-test"):
        for meta in ("stouffer", "fisher"):
            result = GAGEAnalysis().run_gage(
                prepared,
                sets,
                set_size_range=(5, 50),
                test_method=method,
                meta_method=meta,
            )
            rows.append({
                "test_method": method,
                "meta_method": meta,
                "tested_sets": result["greater"].height,
                "top_greater": result["greater"]["gene_set"][0],
                "top_less": result["less"]["gene_set"][0],
                "finite_p_values": bool(np.isfinite(result["greater"]["p_val"].to_numpy().astype(float)).all()),
            })
    pl.DataFrame(rows).write_csv(OUT / "statistic_method_matrix.csv")
    if len(rows) != 6 or not all(row["finite_p_values"] for row in rows):
        raise AssertionError("not every statistic/meta-method combination produced finite results")
    return {"combinations": rows}


def packaged_r_parity() -> dict[str, object]:
    prepared = pl.read_csv(
        UPSTREAM_DATA / "gse16873_prepared.csv.gz",
        schema_overrides={"gene_id": pl.String},
    )
    sets = json.loads((UPSTREAM_DATA / "kegg_gs.json").read_text())
    comparisons = []
    cases = [
        ("t-test", "stouffer", "gage_tTest_greater.csv.gz"),
        ("z-test", "stouffer", "gage_zTest_greater.csv.gz"),
        ("t-test", "fisher", "gage_fisher_greater.csv.gz"),
    ]
    for method, meta, filename in cases:
        got = GAGEAnalysis().run_gage(
            prepared,
            sets,
            test_method=method,
            meta_method=meta,
            compute_effect=False,
        )["greater"]
        expected = pl.read_csv(
            UPSTREAM_DATA / filename,
            null_values="NA",
            infer_schema_length=None,
        ).select(
            "gene_set",
            pl.col("stat.mean").alias("r_stat"),
            pl.col("p.val").alias("r_p"),
        )
        joined = got.join(expected, on="gene_set", how="inner")
        stat_diff = float(np.max(np.abs(
            joined["stat_mean"].to_numpy() - joined["r_stat"].to_numpy()
        )))
        p_diff = float(np.max(np.abs(
            joined["p_val"].to_numpy() - joined["r_p"].to_numpy()
        )))
        comparisons.append({
            "test_method": method,
            "meta_method": meta,
            "common_gene_sets": joined.height,
            "max_abs_stat_difference": stat_diff,
            "max_abs_p_difference": p_diff,
        })
        if stat_diff > 2e-12 or p_diff > 2e-12:
            raise AssertionError(f"R GAGE regression mismatch for {method}/{meta}")
    pl.DataFrame(comparisons).write_csv(OUT / "r_gage_parity.csv")
    return {"comparisons": comparisons}


def new_dataset_classical() -> dict[str, object]:
    source = UPSTREAM_DATA / "GDS3627_exp_formatted.csv"
    expression = read_matrix(source)
    sample_cols = expression.columns[1:]

    def patient(sample: str) -> str:
        return ".".join(sample.split(".")[:3])

    primary = {patient(sample): sample for sample in sample_cols if sample.endswith(".01")}
    normals = [
        sample for sample in sample_cols
        if sample.endswith(".11") and patient(sample) in primary
    ]
    tumors = [primary[patient(sample)] for sample in normals]
    if len(normals) != 13 or len(tumors) != 13:
        raise AssertionError("expected exactly 13 patient-matched normal/tumor pairs")

    pair_table = pl.DataFrame({"patient": [patient(x) for x in normals], "normal": normals, "tumor": tumors})
    pair_table.write_csv(OUT / "new_dataset_13_matched_pairs.csv")
    ref_indices = [sample_cols.index(sample) for sample in normals]
    sample_indices = [sample_cols.index(sample) for sample in tumors]
    prepared = GAGEPreparation.prepare_expression(
        expression,
        ref_indices=ref_indices,
        samp_indices=sample_indices,
        comparison="paired",
        input_logged=True,
    )
    sets = json.loads((UPSTREAM_DATA / "kegg_gs.json").read_text())
    started = time.perf_counter()
    result = GAGEAnalysis().run_gage(
        prepared,
        sets,
        test_method="t-test",
        meta_method="stouffer",
    )
    elapsed = time.perf_counter() - started
    result["greater"].write_csv(OUT / "new_dataset_greater.csv")
    result["less"].write_csv(OUT / "new_dataset_less.csv")
    EnrichmentPlots.bubble_plot(
        result["greater"],
        top_n=15,
        title="New dataset: greater pathways",
        output_file=OUT / "new_dataset_greater_bubble.png",
    )
    return {
        "source_filename": source.name,
        "source_shape": list(expression.shape),
        "sample_suffix_counts": {
            ".01": sum(c.endswith(".01") for c in sample_cols),
            ".11": sum(c.endswith(".11") for c in sample_cols),
            ".06": sum(c.endswith(".06") for c in sample_cols),
        },
        "matched_pairs": 13,
        "prepared_shape": list(prepared.shape),
        "tested_pathways": result["greater"].height,
        "analysis_seconds": round(elapsed, 4),
        "top_greater": result["greater"].head(5)["gene_set"].to_list(),
        "top_less": result["less"].head(5)["gene_set"].to_list(),
        "provenance_note": "The repository filename says GDS3627, but the columns use TCGA identifiers; provenance should be confirmed before publication.",
    }


def command_line_interface() -> dict[str, object]:
    cli = ROOT / ".venv" / "bin" / "pygage"
    env = dict(**__import__("os").environ)
    commands = [
        [
            str(cli), "run", str(DATA / "toy_expression.csv"),
            "--gene-sets", str(DATA / "toy_sets.gmt"),
            "--output", str(OUT / "cli_run.csv"),
            "--ref", "0,1", "--samp", "2,3", "--min-size", "5", "--top", "3",
        ],
        [
            str(cli), "go", str(DATA / "toy_annotations.gaf"),
            "--output", str(OUT / "cli_go.json"),
            "--obo", str(DATA / "toy_go.obo"), "--aspect", "BP", "--propagate",
        ],
    ]
    logs = []
    for command in commands:
        proc = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
        logs.append({"command": command[1], "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
        if proc.returncode != 0:
            raise RuntimeError(f"CLI command failed: {' '.join(command)}\n{proc.stderr}")

    compare = [
        str(cli), "compare", str(OUT / "toy_greater.csv"), str(OUT / "toy_less.csv"),
        "--output", str(OUT / "cli_compare.csv"), "--names", "greater,less", "--q-cutoff", "1",
    ]
    proc = subprocess.run(compare, cwd=ROOT, env=env, text=True, capture_output=True)
    logs.append({"command": "compare", "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return {"commands": logs, "outputs": ["cli_run.csv", "cli_go.json", "cli_compare.csv"]}


def new_chart_compatibility() -> dict[str, object]:
    expression = read_matrix(DATA / "toy_expression.csv")
    prepared = GAGEPreparation.prepare_expression(expression, [0, 1], [2, 3])
    ranked = prepared.select("gene_id", pl.mean_horizontal(pl.exclude("gene_id")).alias("score"))
    fold_changes = dict(zip(ranked["gene_id"], ranked["score"]))
    colors = EnrichmentPlots.pathway_gene_colors(
        [f"g{i:02d}" for i in range(1, 11)],
        fold_changes,
        output_file=OUT / "pathway_gene_colors.png",
    )
    return {"n_gene_colors": len(colors)}


def main() -> int:
    check("toy classical analysis and core plots", toy_analysis)
    check("t/z/KS by Stouffer/Fisher matrix", statistic_matrix)
    check("numeric parity with packaged R GAGE results", packaged_r_parity)
    check("new repository dataset: 13-pair classical analysis", new_dataset_classical)
    check("run/go/compare command-line workflows", command_line_interface)
    check("new pathway gene-color chart", new_chart_compatibility)

    output = OUT / "validation.json"
    output.write_text(json.dumps(REPORT, indent=2, default=str))
    failures = sum(c["status"] == "fail" for c in REPORT["checks"])
    print(f"\nWrote {output}")
    print(f"PyGAGE checks: {len(REPORT['checks']) - failures} passed, {failures} failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
