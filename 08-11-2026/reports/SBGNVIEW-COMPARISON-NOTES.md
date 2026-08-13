# R SBGNview vs. Python Pathview Plus v3

Test date: August 11, 2026

## Bottom line

I tested the official R SBGNview package and Python Pathview Plus v3 on the same frozen SBGN pathway, the same small structural pathway, and the same seven-gene Control/Treatment table. Both programs completed the main workflow: they read the pathway, kept its nodes and arcs, mapped all seven input gene symbols, colored the two conditions as two halves of each mapped node, and wrote SVG and PNG results.

The raw counts agree. A few internal counts look different only because the programs organize the same SBGN objects differently. R keeps compartments, ports, and state variables in its rendering-object list. Python keeps compartments separately, indexes ports to their parent node, and attaches a state variable to its parent instead of treating it as a main node.

## Versions I actually tested

| Part | Tested version |
| --- | --- |
| R | 4.6.1 |
| Bioconductor | 3.23 |
| R SBGNview | 1.26.0 |
| R SBGNview.data | 1.26.0 |
| R rsvg | 2.7.0 |
| System librsvg | 2.62.3 |
| Python | 3.14.3 |
| Python Pathview Plus | 3.1.0 |
| Pathview Plus source commit | `d4d45decec56e1ebec15cf04ae62ff944851780e` |
| Polars | 1.43.2 |
| Matplotlib | 3.11.1 |

Bioconductor 3.23 was the current release for R 4.6 when I ran this test. The official package page lists SBGNview 1.26.0, and the official vignette describes gene/protein and compound mapping, multiple measurements, local SBGN files, and the bundled pathway collection. These are the official references I used:

- [Bioconductor SBGNview package page](https://bioconductor.org/packages/release/bioc/html/SBGNview.html)
- [Official SBGNview vignette](https://bioconductor.org/packages/release/bioc/vignettes/SBGNview/inst/doc/SBGNview.Vignette.html)
- [Official SBGNview quick start](https://bioconductor.org/packages/release/bioc/vignettes/SBGNview/inst/doc/SBGNview.quick.start.html)
- [Official SBGNview reference manual](https://bioconductor.org/packages/release/bioc/manuals/SBGNview/man/SBGNview.pdf)
- [Bioconductor 3.23 release announcement](https://www.bioconductor.org/news/bioc_3_23_release/)
- [RAW Lab Pathview Plus repository](https://github.com/raw-lab/pathview-plus)

## Inputs I kept identical

### P00001 pathway

I used `P00001.new.layout.sbgn` from the frozen Pathview Plus v3 test fixtures. Its SHA-256 is:

```text
b96b3f8536725639f5f9901d22b3dc3a8683295aad7c5cfa6235d08b622fa142
```

That file is byte-for-byte identical to `extdata/P00001.new.layout.sbgn` installed with official R SBGNview 1.26.0. This matters because the comparison is not using a Python-specific remake of the R example.

I also tested `P00001.namespaced.sbgn`. It contains the same pathway but declares the standard SBGN namespace as its default XML namespace.

### Small structural pathway

I used `ports_pd.sbgn` to make the test easy to count by hand. It contains one compartment, four primary glyphs, two ports on one process, one state variable, one clone marker, and three logical arcs. One arc contains an intermediate `next` point.

### Shared biological data

Both programs received this exact matrix from `08-11-2026/data/P00001-shared-control-treatment.csv`:

| Gene symbol | Control | Treatment |
| --- | ---: | ---: |
| COMT | -1.5 | 1.5 |
| DDC | -1.0 | 1.0 |
| TH | -0.5 | 0.5 |
| DBH | 0.0 | 0.0 |
| PNMT | 0.5 | -0.5 |
| SLC18A2 | 1.0 | -1.0 |
| SLC6A3 | 1.5 | -1.5 |

I did not download a live pathway or live mapping table during either run. R used the human rows from its bundled `pathwayCommons_SYMBOL` table. That installed table has 406,940 rows overall and 49,952 human rows. The installed `pathways.info` table has 5,200 pathway records.

## Results

### 1. Default XML namespaces

Both implementations passed this test.

| Check | R SBGNview 1.26.0 | Python Pathview Plus 3.1.0 |
| --- | ---: | ---: |
| Raw P00001 glyph elements | 78 | 78 |
| Raw P00001 arc elements | 83 | 83 |
| Bare and namespaced results match | Yes | Yes |

R produced the same 78 glyph objects and 83 arc objects from both files. Its two namespace-control SVG files are also byte-identical.

Python produced the same ordered glyph IDs, arc IDs, arc classes, endpoints, and spline points from both files. It also produced identical mapped node tables, edge tables, and raster frames from the bare and namespaced files.

### 2. Nodes, compartments, and arcs

For P00001, Python reports 76 primary glyphs plus 2 compartments. R reports all 78 as glyph objects. Both therefore account for the same 78 raw glyph elements.

Python reports 83 logical arcs and resolves all 83 to known endpoints. R builds 83 arc objects. The pathway content is consistent even though the object layouts are different.

### 3. Biological mapping

Both programs used all 7 of the 7 input gene symbols.

| Mapping result | R SBGNview 1.26.0 | Python Pathview Plus 3.1.0 |
| --- | ---: | ---: |
| Input gene symbols used | 7/7 | 7/7 |
| Mapped glyph instances | 12 | 9 |
| Reported eligible pool | 19 macromolecules | 28 gene-class nodes |
| Value columns kept | Control, Treatment | Control, Treatment |

The denominators should not be used as a direct score. R defines the eligible pool as the 19 `macromolecule` glyphs. Python's simplified `gene` pool contains those macromolecules plus 6 complexes and 3 unspecified entities, for 28 total gene-class nodes.

The 9 Python matches are also present in the R result: COMT, DDC, TH, DBH, PNMT, two SLC18A2 glyphs, and two SLC6A3 glyphs. R's bundled Pathway Commons crosswalk expands SLC18A2 to three additional glyph IDs displayed as VAT1, giving R 12 mapped glyph instances. The exact IDs and values are in `python-mapped-nodes.tsv` and `r-mapped-nodes.tsv`.

### 4. The requested half-and-half coloring

Both rendered images show two vertical color bands per mapped glyph:

- Left half: Control
- Right half: Treatment

COMT is an easy visual check. Its Control value is negative and its Treatment value is positive, so it appears green on the left and red on the right. SLC6A3 has the opposite values and appears red on the left and green on the right. DBH is zero in both columns and stays neutral in both halves.

I also checked the stored color data, not only the picture. Python generated `Control_col` and `Treatment_col` for all 9 mapped nodes. R retained both named numeric values on all 12 mapped macromolecule glyphs.

### 5. Ports, state variables, clone markers, and arc geometry

The small structural test shows how each program represents the same details:

| Detail | Frozen XML | R SBGNview | Python Pathview Plus |
| --- | ---: | ---: | ---: |
| Primary biological glyphs | 4 | Included in object list | 4 primary nodes |
| Compartments | 1 | 1 glyph object | 1 separate compartment |
| Ports | 2 | 2 port objects | 2 indexed ports |
| State variables | 1 | 1 state-variable object | 1 attached to its parent |
| Clone markers | 1 | 1 stored clone marker | 1 stored clone marker |
| Logical arcs | 3 | 4 render segments | 3 logical arcs |
| Resolved Python arcs | — | — | 3/3, including 2 through ports |

R turns the arc containing a `next` point into two render segments, so its list has four segments for three logical XML arcs. Python keeps that same intermediate point inside one logical arc. These are two representations of the same route.

R's structural SVG includes the `P@residue` state label and clone graphic. Python's parser preserves the state and clone information in its structured objects; its current general vector output draws the parent nodes without adding those two auxiliary marks. I would treat visual state/clone marks as a focused renderer feature to consider next, while keeping the parser behavior that already passed here.

### 6. Output files

The main files to open are:

- `08-11-2026/results/sbgnview/P00001.new.layout.python-two-state.png`
- `08-11-2026/results/sbgnview/P00001.new.layout.python-two-state.svg`
- `08-11-2026/results/sbgnview/P00001.namespaced.python-two-state.svg`
- `08-11-2026/results/sbgnview/r-two-state_P00001.new.layout.sbgn.png`
- `08-11-2026/results/sbgnview/r-two-state_P00001.new.layout.sbgn.svg`
- `08-11-2026/results/sbgnview/ports_pd.python-structural.svg`
- `08-11-2026/results/sbgnview/r-structural_ports_pd.sbgn.svg`

Every generated file was checked to be non-empty. Exact sizes and SHA-256 values are in:

- `output-manifest-python.tsv`
- `output-manifest-r.tsv`

## How I reproduced it

From the repository root:

```bash
08-11-2026/.venv/bin/python 08-11-2026/scripts/run_python_sbgnview_comparison.py
Rscript 08-11-2026/scripts/run_sbgnview_comparison.R
```

The R script automatically uses the project-local library at `pygage-pathview-validation/.r-library`. SBGNview was not already present there, so I installed the official Bioconductor release and its official data package. On this Mac, PNG conversion also required the system `librsvg` library used by R's `rsvg` package. That is a setup dependency for the extra raster format; SVG is SBGNview's direct output.

The detailed machine-readable evidence is in:

- `python-comparison.json` and `r-comparison.json`
- `python-metrics.tsv` and `r-metrics.tsv`
- `python-mapped-nodes.tsv` and `r-mapped-nodes.tsv`
- `python-node-colors.tsv`
- `r-structural-objects.tsv`

## My conclusion

For this controlled example, Pathview Plus v3 covers the main beginner workflow: load gene data, map it to an SBGN pathway, split a node across multiple conditions, and save the result. The namespace and port-resolution checks are especially important because they show that a normal namespaced SBGN file keeps its complete graph.

The two clearest follow-up features are to carry parsed state/clone marks into Python's vector drawing and to decide whether Python should use the same broader Pathway Commons synonym expansion that produced R's three additional VAT1-labeled matches. Those are specific, testable next steps; the rest of this frozen comparison completed successfully.
