# August 11, 2026 — Pathview Plus v3 comparison

I compared the new Pathview Plus update with R Pathview and R SBGNview. The
main results are below, and all of the code and evidence are in this folder.

## Start here

1. Open the curated, clearly labeled outputs:
   [`outputs-that-matter/00-START-HERE.md`](outputs-that-matter/00-START-HERE.md)
2. Read the special R comparison README:
   [`README-R-VS-PYTHON.md`](README-R-VS-PYTHON.md)
3. Open the fully run Jupyter notebook:
   [`notebooks/executed/01-pathview-v3-vs-r-and-sbgnview.executed.ipynb`](notebooks/executed/01-pathview-v3-vs-r-and-sbgnview.executed.ipynb)
4. Read the short result:
   [`COMPARISON-SUMMARY.md`](COMPARISON-SUMMARY.md)
5. Read what I did today:
   [`08-11-2026-WORK-LOG.md`](08-11-2026-WORK-LOG.md)

The notebook is a real `.ipynb`, not a Markdown file renamed as one. Its 11
code cells all ran, with 0 unexecuted cells and 0 error outputs. The verification
is in [`notebooks/execution-report.json`](notebooks/execution-report.json).

## The comparison

| Comparison | What matched | What was different |
|---|---|---|
| R Pathview vs Pathview Plus | All 5 shared genes, condition order, raw map size, and gene + compound mapping | Grouped KEGG rows and compound-circle size |
| R SBGNview vs Pathview Plus | All 7 shared genes, 78 total glyphs, 83 arcs, and condition order | SLC18A2/VAT1 aliases and drawing state/clone marks |

Basically, the main workflows worked. I also rechecked my August 10 list: 60
findings are fixed, 19 still happen, and 7 are handled differently now.

The test totals were **321 passed, 6 skipped, 0 failed** in the Pathview Plus
suite and **16 passed, 0 failed** in my own Python checks.

## What is in this folder

| Folder or file | What it contains |
|---|---|
| `notebooks/` | Beginner-readable source notebook and fully executed copy |
| `data/` | Small controlled CSV files used by both R and Python |
| `scripts/` | Reproducible Python, R Pathview, R SBGNview, and notebook runners |
| `reports/` | Detailed R, Python, SBGN, and v3 change notes |
| `results/python-pathview/` | Python checks, images, tables, hashes, and JSON |
| `results/r-pathview/` | R Pathview checks, images, node tables, and JSON |
| `results/sbgnview/` | R/Python SBGN figures, metrics, mapped nodes, and JSON |
| `results/v3-audit/` | Status of all 86 August 10 findings and JUnit evidence |
| `results/pathview-plus-v3-upstream-junit.xml` | Final upstream test result |
| `COMPARISON-SUMMARY.md` | Main result in plain language |
| `SETUP-AND-RERUN.md` | Exact rerun instructions |

The local `.venv`, caches, installed R library, and cloned source are ignored
so they are not accidentally committed as hundreds of megabytes.

## Detailed reports

- [`reports/PYTHON-PATHVIEW-COMPARISON-NOTES.md`](reports/PYTHON-PATHVIEW-COMPARISON-NOTES.md)
- [`reports/R-PATHVIEW-COMPARISON-NOTES.md`](reports/R-PATHVIEW-COMPARISON-NOTES.md)
- [`reports/SBGNVIEW-COMPARISON-NOTES.md`](reports/SBGNVIEW-COMPARISON-NOTES.md)
- [`reports/V3-CHANGE-AUDIT.md`](reports/V3-CHANGE-AUDIT.md)

## Important scope note

The Pathview Plus repository has its own 74-row feature matrix reporting 97.0%
coverage versus R Pathview and 98.1% versus R SBGNview. I saved that matrix,
but I label those numbers as **project-declared feature coverage**. The frozen
R/Python runs in this folder are my independent comparison.

I did not edit Pathview Plus source code. The pinned source checkout stayed
clean. I also did not change anything inside `08-10-2026` during this work.
