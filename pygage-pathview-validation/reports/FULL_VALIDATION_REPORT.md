# Full validation report: PyGAGE and Pathview

**Validation date:** August 10, 2026  
**Scope:** current repository heads for `raw-lab/pygage` and `raw-lab/pathview-plus`, plus current Bioconductor R pathview.

## Executive result

The requested Jupyter deliverable is complete and executed. Four notebooks run without cell errors:

1. `00_START_HERE.ipynb`
2. `01_pygage_full_validation.ipynb`
3. `02_pathview_plus_full_validation.ipynb`
4. `03_r_vs_python_pathview.ipynb`

The controlled half-and-half comparison passed. R pathview and Python Pathview Plus used the same frozen `hsa04110` KGML and PNG, mapped the same three controlled rows to the same coordinates, preserved the same `Classical, Basal` column order, and produced the expected left-green/right-red node.

The offline assertion suite produced **41 passed checks and 8 expected compatibility findings**, with no unexpected failures. In addition:

- PyGAGE workflow: **5 passed**, 1 current compatibility finding.
- Python Pathview workflow: **7 passed**, 0 failed, 5 live-service checks not run.
- R pathview workflow: **7 passed**, 0 failed.
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
| Python | 3.14.3 |
| R | R version 4.6.1 (2026-06-24) |

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

The t/Stouffer, z/Stouffer, and t/Fisher results were joined to the packaged R GAGE reference tables across 160 common tested pathways. The largest absolute p-value difference was **2.11e-15**, consistent with floating-point rounding at approximately machine precision.

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
