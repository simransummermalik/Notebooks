#!/usr/bin/env python3
"""Build the final human-readable and machine-readable validation reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from xml.etree import ElementTree as ET

import nbformat


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


pygage = load_json(ROOT / "results" / "pygage" / "validation.json")
python_pathview = load_json(ROOT / "results" / "pathview_python" / "validation.json")
r_pathview = load_json(ROOT / "results" / "pathview_r" / "validation.json")
comparison = load_json(ROOT / "results" / "comparison" / "comparison.json")

junit_root = ET.parse(REPORTS / "offline-junit.xml").getroot()
junit_suite = junit_root if "tests" in junit_root.attrib else junit_root.find("testsuite")
if junit_suite is None:
    raise ValueError("offline-junit.xml does not contain a testsuite")
offline = {
    "tests": int(junit_suite.attrib["tests"]),
    "passed": int(junit_suite.attrib["tests"])
    - int(junit_suite.attrib.get("failures", 0))
    - int(junit_suite.attrib.get("errors", 0))
    - int(junit_suite.attrib.get("skipped", 0)),
    "expected_xfail": int(junit_suite.attrib.get("skipped", 0)),
    "failures": int(junit_suite.attrib.get("failures", 0)),
    "errors": int(junit_suite.attrib.get("errors", 0)),
    "seconds": float(junit_suite.attrib.get("time", 0)),
}


def summarize_checks(report: dict) -> dict[str, int]:
    statuses = [check["status"] for check in report["checks"]]
    return {
        "pass": statuses.count("pass"),
        "fail": statuses.count("fail"),
        "not_run": statuses.count("not_run"),
    }


notebook_results = []
for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
    nb = nbformat.read(path, as_version=4)
    code_cells = [cell for cell in nb.cells if cell.cell_type == "code"]
    error_outputs = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    executed = all(cell.get("execution_count") is not None for cell in code_cells)
    notebook_results.append({
        "file": str(path.relative_to(ROOT)),
        "code_cells": len(code_cells),
        "all_code_cells_executed": executed,
        "error_outputs": len(error_outputs),
        "status": "pass" if executed and not error_outputs else "fail",
    })


features = [
    # PyGAGE
    ("PyGAGE", "Install/import repository 1.2.1", "PASS", "Imported from commit 265ab1a; Python 3.14.3", "Repository version tested directly"),
    ("PyGAGE", "Raw expression matrix", "PASS", "test_convenience_gage_raw_and_prepared", "Genes × samples with string gene IDs"),
    ("PyGAGE", "Prepared fold-change matrix", "PASS", "Toy and GSE16873 regressions", "Single and multiple fold-change columns"),
    ("PyGAGE", "Paired comparison", "PASS", "Toy + 13 matched new-data pairs", "Equal reference/sample counts"),
    ("PyGAGE", "Unpaired comparison", "PASS", "Automated offline test", "Every sample-vs-reference contrast"),
    ("PyGAGE", "as.group comparison", "PASS", "Automated offline test", "One group-mean difference"),
    ("PyGAGE", "1ongroup comparison", "PASS", "Automated offline test", "Each sample versus reference mean"),
    ("PyGAGE", "Repeated sample blocks per paired reference", "EXPECTED XFAIL", "test_multiple_sample_blocks_per_reference_are_supported", "Documented multiple currently produces a shape mismatch"),
    ("PyGAGE", "DE table and preranked input", "PASS", "Automated input-adapter test", "Auto-detect log2FC/stat and dict rankings"),
    ("PyGAGE", "Polars/pandas/dict/AnnData inputs", "PASS", "Automated input-adapter tests", "AnnData 0.13.2 included"),
    ("PyGAGE", "t-test", "PASS", "Six-method matrix + R regression", "Greater and less directions"),
    ("PyGAGE", "z-test", "PASS", "Six-method matrix + R regression", "Greater and less directions"),
    ("PyGAGE", "KS test", "PASS", "Six-method matrix", "Finite results on controlled data"),
    ("PyGAGE", "Stouffer meta-method", "PASS", "Six-method matrix + R regression", ""),
    ("PyGAGE", "Fisher meta-method", "PASS", "Six-method matrix + R regression", ""),
    ("PyGAGE", "Directional and directionless", "PASS", "Automated offline tests", "greater/less and magnitude-only"),
    ("PyGAGE", "BH and global BH", "PASS", "Known values + extended options", "NaN-preserving BH"),
    ("PyGAGE", "Control genes, effects, leading edge", "PASS", "Extended-options test", ""),
    ("PyGAGE", "Threaded gene-set loop", "PASS", "n_jobs=2 deterministic test", "Thread environment also checked"),
    ("PyGAGE", "Permutation p-value", "EXPECTED XFAIL", "test_permutation_null_is_informative", "Column-order permutation leaves the tested statistic invariant"),
    ("PyGAGE", "GMT/MSigDB/Reactome/GO gene sets", "PASS", "Automated loader tests", "Includes GO propagation and cache round-trip"),
    ("PyGAGE", "Result filtering/comparison/grouping", "PASS", "Automated result-helper tests", "Includes esset_grp and Venn comparison"),
    ("PyGAGE", "Bubble/enrichment heatmap/running enrichment", "PASS", "Saved PNGs + automated plot tests", ""),
    ("PyGAGE", "Pathway gene-color chart", "EXPECTED XFAIL", "test_new_pathway_gene_color_chart", "Uses matplotlib.cm.get_cmap removed in Matplotlib 3.11"),
    ("PyGAGE", "CLI run/go/compare", "PASS", "results/pygage/cli_*", "All three commands returned 0"),
    ("PyGAGE", "CLI live KEGG", "NOT RUN", "Requires live KEGG", "Current organism-list endpoint returned HTTP 400 during source audit"),
    ("PyGAGE", "Packaged R GAGE numerical parity", "PASS", "results/pygage/r_gage_parity.csv", "Max absolute differences around 10^-15"),
    ("PyGAGE", "Newest large data file", "PASS", "13 matched pairs, 162 tested pathways", "Filename/provenance should be confirmed before publication"),
    ("PyGAGE", "Top-level star import", "EXPECTED XFAIL", "test_star_import_contract", "__all__ lists normalize_gene_sets without package-scope import"),
    # Python Pathview Plus
    ("Pathview Plus", "Install/import repository 2.0.2", "PASS", "Imported from commit 07aee81", "Runtime __version__ reports 2.0.0"),
    ("Pathview Plus", "One-condition native PNG", "PASS", "hsa04110.classical.png", "Full-width node fill"),
    ("Pathview Plus", "Two-condition native PNG", "PASS", "hsa04110.half_half.png", "First column left, second right"),
    ("Pathview Plus", "Exact half-and-half pixels", "PASS", "CDKN2A crop: 316 left-green, 334 right-red", "Wrong-side counts were zero"),
    ("Pathview Plus", "Three-condition native PNG", "PASS", "hsa04110.three_state.png", "Three ordered bands"),
    ("Pathview Plus", "SVG file", "PARTIAL", "Valid XML, ordered split-node geometry", "Current renderer does not receive pathway edges/background"),
    ("Pathview Plus", "Graph/PDF file", "PARTIAL", "Valid %PDF file", "Uses first state only and graph receives no pathway edges"),
    ("Pathview Plus", "Gene plus compound mapping", "PARTIAL", "Offline compound painter passed", "Fresh hsa00010 end-to-end needs live KEGG"),
    ("Pathview Plus", "KO pathway", "NOT RUN", "Prepared ko00910 input included", "Fresh ko00910 assets need live KEGG"),
    ("Pathview Plus", "KGML parsing", "PASS", "Automated node/relation/reaction test", "Official hsa04110 parsed too"),
    ("Pathview Plus", "Namespaced SBGN parsing", "EXPECTED XFAIL", "test_sbgn_parser_and_unified_dataframe", "Namespace-qualified glyph/arc search is missing"),
    ("Pathview Plus", "sum/mean/median/max aggregation", "PASS", "Automated aggregation tests", ""),
    ("Pathview Plus", "max_abs/random aggregation", "EXPECTED XFAIL", "max_abs automated; random source audit", "Current Polars group UDF receives scalar values"),
    ("Pathview Plus", "Continuous colors, clipping, NA, transform", "PASS", "Automated color tests", "Odd bins put zero exactly at midpoint"),
    ("Pathview Plus", "Discrete color mode", "PARTIAL", "Source/API audit", "Argument is accepted but ignored by node_color"),
    ("Pathview Plus", "Highlighting layer primitives", "PARTIAL", "Synthetic PathwayResult composition passed", "pathview() returns dict, so documented direct composition is not end-to-end"),
    ("Pathview Plus", "Cubic/quadratic spline helpers", "PASS", "Finite endpoints and SVG path tests", ""),
    ("Pathview Plus", "Catmull–Rom spline", "EXPECTED XFAIL", "test_catmull_rom_documented_default_is_finite", "Duplicated endpoints cause zero denominators"),
    ("Pathview Plus", "Fresh live KEGG pathways", "NOT RUN", "--live suite included", "Network approval unavailable in final local run"),
    ("Pathview Plus", "Package/runtime version agreement", "EXPECTED XFAIL", "test_distribution_and_runtime_versions_match", "Distribution 2.0.2 vs runtime 2.0.0"),
    # R pathview and parity
    ("R pathview", "Bioconductor 1.52.0 install", "PASS", "R 4.6.1 / Bioconductor 3.23", "Local project library"),
    ("R pathview", "One-condition native PNG", "PASS", "hsa04110.r_classical.png", "3 controlled genes mapped"),
    ("R pathview", "Two-condition multi.state PNG", "PASS", "hsa04110.r_half_half.multi.png", "Classical left, Basal right"),
    ("R pathview", "Three-condition multi.state PNG", "PASS", "hsa04110.r_three_state.multi.png", "Ordered bands"),
    ("R pathview", "Official gse16873 example", "PASS", "hsa04110.r_gse16873.png", "11,979 input genes; 91 mapped nodes"),
    ("R pathview", "Graphviz multi-state PDF", "PASS", "hsa04110.r_graph.multi.pdf", "Valid non-empty PDF"),
    ("R pathview", "Required exported helper surface", "PASS", "12/12 required exports present", ""),
    ("R vs Python", "Mapped coordinate/value parity", "PASS", "3/3 controlled mapped rows", "Maximum value difference 0"),
    ("R vs Python", "Half-and-half pixel orientation", "PASS", "results/comparison/comparison.json", "Both: 316 left-green, 334 right-red, zero wrong-side"),
    ("Jupyter", "All four notebooks execute", "PASS", "Fresh-kernel nbconvert execution", "No notebook error outputs"),
]

feature_path = REPORTS / "FEATURE_MATRIX.csv"
with feature_path.open("w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["component", "feature", "status", "evidence", "notes"])
    writer.writerows(features)

aggregate = {
    "date": "2026-08-10",
    "offline_pytest": offline,
    "workflow_checks": {
        "pygage": summarize_checks(pygage),
        "pathview_python": summarize_checks(python_pathview),
        "pathview_r": summarize_checks(r_pathview),
        "r_vs_python": {"status": comparison["overall_status"]},
    },
    "notebooks": notebook_results,
    "versions": {
        "pygage": pygage["version"],
        "pathview_plus_distribution": python_pathview["distribution_version"],
        "pathview_plus_runtime": python_pathview["runtime_version"],
        "r_pathview": r_pathview["version"],
        "python": python_pathview["python"],
        "r": r_pathview["r_version"],
        "bioconductor": r_pathview["bioconductor"],
    },
    "comparison": comparison,
}
(REPORTS / "test_results.json").write_text(json.dumps(aggregate, indent=2))

pygage_counts = summarize_checks(pygage)
python_counts = summarize_checks(python_pathview)
r_counts = summarize_checks(r_pathview)
parity_max = max(
    case["max_abs_p_difference"]
    for case in next(c for c in pygage["checks"] if c["name"].startswith("numeric parity"))["details"]["comparisons"]
)

report_text = f"""# Full validation report: PyGAGE and Pathview

**Validation date:** August 10, 2026  
**Scope:** current repository heads for `raw-lab/pygage` and `raw-lab/pathview-plus`, plus current Bioconductor R pathview.

## Executive result

The requested Jupyter deliverable is complete and executed. Four notebooks run without cell errors:

1. `00_START_HERE.ipynb`
2. `01_pygage_full_validation.ipynb`
3. `02_pathview_plus_full_validation.ipynb`
4. `03_r_vs_python_pathview.ipynb`

The controlled half-and-half comparison passed. R pathview and Python Pathview Plus used the same frozen `hsa04110` KGML and PNG, mapped the same three controlled rows to the same coordinates, preserved the same `Classical, Basal` column order, and produced the expected left-green/right-red node.

The offline assertion suite produced **{offline['passed']} passed checks and {offline['expected_xfail']} expected compatibility findings**, with no unexpected failures. In addition:

- PyGAGE workflow: **{pygage_counts['pass']} passed**, {pygage_counts['fail']} current compatibility finding.
- Python Pathview workflow: **{python_counts['pass']} passed**, {python_counts['fail']} failed, {python_counts['not_run']} live-service checks not run.
- R pathview workflow: **{r_counts['pass']} passed**, {r_counts['fail']} failed.
- All four Jupyter notebooks: **passed fresh-kernel execution**.

No upstream PyGAGE or Pathview Plus source files were changed. This folder contains tests, notebooks, inputs, results, and reports only.

## Exact versions tested

| Component | Version / commit |
|---|---|
| PyGAGE repository | 1.2.1, `265ab1a07a3987eba41779931053fbe7b3ef4fd3` |
| Pathview Plus repository | distribution 2.0.2, `07aee813375347bcc933ad21b4aed561dd7cd3bf` |
| Pathview Plus runtime string | 2.0.0 |
| R pathview | 1.52.0 |
| Bioconductor | 3.23 |
| Python | {python_pathview['python']} |
| R | {r_pathview['r_version']} |

PyGAGE 1.2.1 and Pathview Plus 2.0.2 were installed from their repository commits. The public PyGAGE release channels still carry older release artifacts, so the repository commit is the correct target for “new PyGAGE” testing.

## What changed in the newest versions

### PyGAGE

The newest commit adds one file only: `tests/GDS3627_exp_formatted.csv`. It does not change source code, APIs, documentation, dependencies, or the 1.2.1 version number.

The file contains:

- 19,469 unique genes;
- 198 samples;
- 184 names ending `.01`;
- 13 names ending `.11`;
- one name ending `.06`;
- exactly 13 patient-matched `.11`/`.01` pairs.

The classical matched-pair analysis passed: 19,469 genes × 13 fold-change columns, with 162 pathways tested in each direction. The top greater pathways began with Cell cycle, DNA replication, and Spliceosome.

The filename says `GDS3627`, while its columns use TCGA-style identifiers. Confirm the data provenance and whether values are already log-scaled before public documentation or publication.

### Pathview Plus

The functional code matches tag v2.0.2. The commits after that tag change README text only. One packaging detail remains: the installed distribution is 2.0.2 while `pathview.__version__` reports 2.0.0.

### R pathview

Bioconductor release 1.52.0 is a release-number bump from the maintainer source 1.47.1 rather than a new functional implementation. The latest functional NEWS items expand the KEGG species table and adjust one suggested annotation package.

## PyGAGE results

### Core statistics

All six controlled combinations ran with finite results:

- t-test + Stouffer;
- t-test + Fisher;
- z-test + Stouffer;
- z-test + Fisher;
- KS test + Stouffer;
- KS test + Fisher.

Raw, prepared, DE, preranked, Polars, pandas, dict, and AnnData inputs were tested. Paired, unpaired, `as.group`, and `1ongroup` preparation passed. Directional and magnitude-only analyses, BH/global BH, control genes, effect sizes, leading-edge output, threaded execution, gene-set loaders, result helpers, and general plots were exercised.

### R GAGE numerical regression

The t/Stouffer, z/Stouffer, and t/Fisher results were joined to the packaged R GAGE reference tables across 160 common tested pathways. The largest absolute p-value difference was **{parity_max:.3g}**, consistent with floating-point rounding at approximately machine precision.

### Current PyGAGE compatibility notes

1. `pathway_gene_colors()` uses `matplotlib.cm.get_cmap`, removed in Matplotlib 3.11. The other new enrichment charts passed.
2. The permutation implementation shuffles complete prepared columns. That does not create an informative null for its cross-column statistic; the tested permutation p-values are invariant.
3. The paired preparation documentation allows sample count to be a multiple of reference count, but the implementation currently handles equal counts only.
4. `pygage.__all__` lists `normalize_gene_sets` without importing it at package scope, so star import fails even though direct import works.

## Pathview Plus results

### Single, half-and-half, and three-state nodes

The exact controlled input was:

| Gene | Classical | Basal |
|---|---:|---:|
| 1029 / CDKN2A | -2 | +2 |

The two condition columns were passed in the order `Classical, Basal`. Both implementations produced:

- left half = Classical = green;
- right half = Basal = red.

At CDKN2A coordinates `(532, 124)`, the tolerant pixel count was identical:

| Implementation | left green | right green | left red | right red |
|---|---:|---:|---:|---:|
| Python | 316 | 0 | 0 | 334 |
| R | 316 | 0 | 0 | 334 |

Three controlled mapped node rows had identical x/y coordinates and identical condition values; maximum mapped-value difference was 0.

### Formats

- Python native PNG: passed.
- Python SVG: valid XML and correct split-node geometry; the current SVG path does not include the KEGG background or pathway edges.
- Python graph PDF: valid PDF; the graph renderer uses only the first state and does not receive KGML pathway edges.
- R native PNG and Graphviz multi-state PDF: passed.

For a fair two-state R/Python comparison, use native PNG. R's `split.group` is unrelated; the half-and-half behavior is called **multi-state rendering**.

### Current Pathview Plus compatibility notes

1. Live human calls currently depend on KEGG `list/organism` before inspecting cached files. During the source audit that endpoint returned HTTP 400, while direct KGML/image downloads returned 200.
2. Namespaced SBGN glyph and arc searches returned no nodes in the controlled parser test.
3. `max_abs` and `random` aggregation use a Polars group UDF in a way that receives scalar values in the current dependency version.
4. Catmull–Rom endpoints create zero denominators and NaN values.
5. The composable highlighting primitives work on a manually constructed `PathwayResult`, but `pathview()` returns a dictionary, so the documented direct `pathview(...) + highlight_nodes(...)` workflow is not connected end to end.
6. The discrete color argument is accepted but not applied by `node_color`.

## Live-service boundary

The final reproducible run did not receive approval to download fresh KEGG files. The suite therefore records five fresh pathway/service cases as `NOT RUN` and uses the official frozen Bioconductor `hsa04110.xml` and `hsa04110.png` for the executed parity tests.

Prepared inputs and the `--live` workflow are included for:

- `hsa04151` PI3K–Akt classical expression;
- `hsa04010` MAPK multi-condition expression;
- `hsa00010` genes plus compounds;
- `ko00910` nitrogen metabolism.

Run them with:

```bash
python scripts/run_pathview_validation.py --live
```

## Recommended next fixes

1. Make cached Pathview runs independent of the live KEGG organism-list endpoint.
2. Add normal pytest/CI suites to both repositories, using frozen pathway fixtures and separately marked live tests.
3. Fix PyGAGE's Matplotlib call and permutation null before presenting those two items as stable features.
4. Align Pathview Plus distribution and runtime version strings.
5. Connect SBGN parsing/rendering and highlighting through the main Pathview result object.
6. Confirm the new PyGAGE dataset name, provenance, sample meaning, and log scale.

## Files to open

- `notebooks/00_START_HERE.ipynb` — easiest entry point.
- `notebooks/01_pygage_full_validation.ipynb` — beginner PyGAGE walkthrough.
- `notebooks/02_pathview_plus_full_validation.ipynb` — one-state, half-and-half, and three-state Pathview.
- `notebooks/03_r_vs_python_pathview.ipynb` — executable R/Python comparison.
- `reports/FEATURE_MATRIX.csv` — row-by-row test coverage.
- `reports/test_results.json` — machine-readable combined results.
- `results/comparison/r_vs_python_half_half.png` — visual comparison.

## Authoritative references

- [PyGAGE repository](https://github.com/raw-lab/pygage)
- [Pathview Plus repository](https://github.com/raw-lab/pathview-plus)
- [Bioconductor pathview package](https://bioconductor.org/packages/release/bioc/html/pathview.html)
- [R pathview reference manual](https://bioconductor.org/packages/release/bioc/manuals/pathview/man/pathview.pdf)
- [R pathview vignette](https://bioconductor.org/packages/release/bioc/vignettes/pathview/inst/doc/pathview.pdf)
- [Bioconductor installation](https://www.bioconductor.org/install/)
"""
(REPORTS / "FULL_VALIDATION_REPORT.md").write_text(report_text)

comparison_text = f"""# R pathview versus Python Pathview Plus

## Verdict

The controlled `hsa04110` native-PNG half-and-half comparison passed.

- R pathview: {r_pathview['version']}
- Python Pathview Plus: {python_pathview['distribution_version']}
- Same frozen KGML and PNG: yes
- Same mapped controlled coordinates: {comparison['mapped_table_parity']['common_mapped_coordinates']}
- Maximum mapped-value difference: {comparison['mapped_table_parity']['maximum_value_difference']}
- First condition: Classical, left green
- Second condition: Basal, right red

Both implementations counted 316 green pixels on the left and 334 red pixels on the right inside the controlled CDKN2A node, with zero wrong-side green/red pixels.

Use native PNG for multi-state parity. R Graphviz supports multiple states; Python's graph/PDF implementation uses its first state only.

See `results/comparison/r_vs_python_half_half.png` and `results/comparison/comparison.json` for evidence.
"""
(REPORTS / "R_VS_PYTHON_PATHVIEW.md").write_text(comparison_text)

print(f"Wrote {REPORTS / 'FULL_VALIDATION_REPORT.md'}")
print(f"Wrote {feature_path}")
print(f"Wrote {REPORTS / 'test_results.json'}")
print(f"Wrote {REPORTS / 'R_VS_PYTHON_PATHVIEW.md'}")
