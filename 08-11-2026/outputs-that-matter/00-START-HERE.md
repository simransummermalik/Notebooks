# Outputs that matter

This folder contains labeled copies of the outputs I used most from the August
11, 2026 comparison. The original files in `08-11-2026/results/`, `reports/`,
and `notebooks/` were left in place.

## What was compared

- Python Pathview Plus 3.1.0 versus R pathview 1.52.0 on KEGG pathways.
- Python Pathview Plus 3.1.0 versus R SBGNview 1.26.0 on an SBGN pathway.
- One condition, two-condition left/right coloring, three conditions, genes plus compounds, pathway structure, identifier mapping, and output formats.

## Open these first

1. [`01-key-figures/01-r-pathview-vs-python-pathview-cell-cycle.png`](01-key-figures/01-r-pathview-vs-python-pathview-cell-cycle.png) — the main R pathview versus Python Pathview Plus KEGG comparison.
2. [`01-key-figures/05-python-pathview-half-and-half-CDKN2A-closeup.png`](01-key-figures/05-python-pathview-half-and-half-CDKN2A-closeup.png) — the clearest Python proof that the first condition is on the left and the second is on the right.
3. [`01-key-figures/06-r-pathview-half-and-half-CDKN2A-closeup.png`](01-key-figures/06-r-pathview-half-and-half-CDKN2A-closeup.png) — the matching R pathview close-up.
4. [`01-key-figures/13-python-pathview-plus-sbgn-two-condition.png`](01-key-figures/13-python-pathview-plus-sbgn-two-condition.png) — the Python Pathview Plus SBGN result.
5. [`01-key-figures/14-r-sbgnview-two-condition.png`](01-key-figures/14-r-sbgnview-two-condition.png) — the R SBGNview result using the same pathway and data.
6. [`03-proof-and-reports/06-executed-comparison-notebook.ipynb`](03-proof-and-reports/06-executed-comparison-notebook.ipynb) — the fully executed Jupyter notebook.

## Color and condition labels

- Green represents a negative value.
- Gray represents a value near zero.
- Red represents a positive value.
- In two-condition figures, the first column (`Control` or `Classical`) is the left half.
- The second column (`Treatment` or `Basal`) is the right half.

## 01-key-figures

| Label | File | What it shows |
|---:|---|---|
| 01 | `01-r-pathview-vs-python-pathview-cell-cycle.png` | Main side-by-side Cell Cycle comparison: R pathview on the left and Python Pathview Plus on the right. |
| 02 | `02-r-vs-python-pathview-pixel-difference.png` | Pixel-difference view showing where the two KEGG renderings vary. |
| 03 | `03-python-pathview-one-condition.png` | Python Pathview Plus with one condition filling each mapped node. |
| 04 | `04-python-pathview-two-condition-half-and-half.png` | Python Pathview Plus with two conditions split left and right. |
| 05 | `05-python-pathview-half-and-half-CDKN2A-closeup.png` | Python CDKN2A close-up used to verify left/right color order. |
| 06 | `06-r-pathview-half-and-half-CDKN2A-closeup.png` | R pathview CDKN2A close-up used for the same order check. |
| 07 | `07-python-pathview-three-condition.png` | Python Pathview Plus with three ordered condition bands. |
| 08 | `08-r-pathview-three-condition-CDKN2A-closeup.png` | R pathview three-condition CDKN2A close-up. |
| 09 | `09-r-vs-python-pathview-gene-and-compound.png` | Controlled gene-and-compound comparison using the same hsa00020 inputs. |
| 10 | `10-python-pathview-highlighted-pathway.png` | Python Pathview Plus highlighting output. |
| 11 | `11-python-pathview-vector-output.svg` | Python vector SVG output. |
| 12 | `12-r-pathview-graph-output.pdf` | R pathview graph-based PDF output. |
| 13 | `13-python-pathview-plus-sbgn-two-condition.png` | Python Pathview Plus SBGN pathway with Control and Treatment. |
| 14 | `14-r-sbgnview-two-condition.png` | R SBGNview result from the same SBGN pathway and shared data. |
| 15 | `15-python-pathview-plus-sbgn-two-condition.svg` | Editable Python SBGN SVG output. |
| 16 | `16-r-sbgnview-two-condition.svg` | Editable R SBGNview SVG output. |
| 17 | `17-python-sbgn-structural-details.svg` | Python structural SBGN test covering ports, state data, clone data, and arcs. |
| 18 | `18-r-sbgnview-structural-details.svg` | R SBGNview output for the same small structural pathway. |

## 02-data-and-tables

| Label | File | What it contains |
|---:|---|---|
| 01 | `01-pathview-shared-input.csv` | Exact five-gene Control/Treatment input used by R pathview and Python Pathview Plus. |
| 02 | `02-python-pathview-selected-nodes.csv` | Python mapped KEGG rows for the shared input. |
| 03 | `03-r-pathview-selected-nodes.csv` | R mapped KEGG rows for the shared input. |
| 04 | `04-python-pathview-check-results.csv` | One row for each independent Python check. |
| 05 | `05-r-pathview-check-results.csv` | One row for each R pathview check. |
| 06 | `06-sbgn-shared-input.csv` | Exact seven-gene-symbol Control/Treatment input used by both SBGN workflows. |
| 07 | `07-python-sbgn-mapped-nodes.tsv` | Python gene-to-glyph mappings. |
| 08 | `08-r-sbgnview-mapped-nodes.tsv` | R SBGNview gene-to-glyph mappings. |
| 09 | `09-python-sbgn-node-colors.tsv` | Python Control and Treatment colors assigned to mapped glyphs. |
| 10 | `10-python-sbgn-metrics.tsv` | Main Python SBGN counts and measurements. |
| 11 | `11-r-sbgnview-metrics.tsv` | Main R SBGNview counts and measurements. |
| 12--15 | `*-comparison.json` | Full machine-readable comparison evidence for each implementation. |

## 03-proof-and-reports

| Label | File | What it proves |
|---:|---|---|
| 01 | `01-comparison-summary.md` | Short plain-language conclusion. |
| 02 | `02-r-vs-python-readme.md` | Main labeled comparison with key figures. |
| 03 | `03-python-pathview-detailed-notes.md` | Detailed Python Pathview Plus method and evidence. |
| 04 | `04-r-pathview-detailed-notes.md` | Detailed R pathview method and evidence. |
| 05 | `05-sbgnview-detailed-notes.md` | Detailed R SBGNview versus Python SBGN evidence. |
| 06 | `06-executed-comparison-notebook.ipynb` | Complete notebook with saved outputs. |
| 07 | `07-notebook-execution-proof.json` | Confirms 11 of 11 code cells ran with zero errors. |
| 08 | `08-pathview-plus-test-summary.txt` | Short upstream test output. |
| 09 | `09-pathview-plus-test-results.xml` | Machine-readable upstream test results. |

## Main result

In the saved checks, Python Pathview Plus matched the R tools on the shared
inputs, condition order, core pathway structure, multi-condition coloring, and
main output generation. I kept the measured implementation differences in the
reports so they are easy to find.
