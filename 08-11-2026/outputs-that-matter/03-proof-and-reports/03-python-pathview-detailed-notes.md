# My Pathview Plus v3 checks — August 11, 2026

## Bottom line

I tested the exact current Pathview Plus update, not an older local copy. I
checked version **3.1.0** at commit
`d4d45decec56e1ebec15cf04ae62ff944851780e`.

My independent Python comparison finished with **16 passes and 0 failures**.
The package's own full test suite finished with **321 passes, 6 skips, and 0
failures**. I also ran the smaller bundled smoke test, which finished with **11
passes and 0 failures**.

The main things I personally confirmed were:

- One condition colors a whole node.
- Two conditions split the node left and right.
- Three conditions split the node into three ordered bands.
- Genes and compounds can be shown on the same pathway with separate color
  scales.
- Native, vector, graph, automatic, PNG, PDF, and SVG outputs all produced
  real files.
- Namespaced SBGN files, arcs through ports, state variables, clone markers,
  and compartments parsed correctly in the controlled fixtures.
- A two-condition SBGN dataset mapped all 7 input gene symbols and colored 9
  pathway glyph rows.
- Batch rendering, highlighting, label changes, complex splitting, and
  multi-gene node expansion worked in the controlled runs.
- The command-line interface worked offline with the same local files.

The full evidence is in `../results/python-pathview/comparison.json`. The flat
pass/fail table is in `../results/python-pathview/check-results.csv`.

## How I made the R/Python comparison fair

I used the same frozen `hsa04110.xml` and `hsa04110.png` for R Pathview and
Pathview Plus. Their SHA-256 hashes matched byte for byte. That matters because
otherwise a pathway update could look like a software difference.

I also gave both programs this exact Control/Treatment table:

| Entrez ID | Control | Treatment |
|---:|---:|---:|
| 1017 | -1.5 | 1.5 |
| 1019 | -0.7 | 0.7 |
| 1021 | 0.0 | 0.0 |
| 595 | 0.8 | -0.8 |
| 7157 | 1.4 | -1.4 |

Both programs used all five IDs. Both raw maps were **1039 x 801 pixels**, so I
could compare the same coordinate system directly. About **90.16% of pixels
were identical**. The mean absolute channel difference was only **1.39 out of
255**. Most changed pixels were the expected colored node areas and small
renderer/style differences.

The easiest picture to inspect is
`../results/python-pathview/figures/hsa04110.R-vs-Python.shared-side-by-side.png`.
The amplified difference image is beside it in the same folder.

R and Python do not return exactly the same number of node-table rows for this
input. R's selected table has 5 rows, while Pathview Plus reports 8 pathway
nodes carrying data. All five requested biological IDs were still used. This
looks like a difference in how repeated and grouped KEGG entries are represented,
so I kept both node tables instead of hiding the difference.

## One, two, and three conditions

I used CDKN2A (Entrez 1029) as the strongest visual proof because it has a
known node at x=532, y=124, width=46, and height=17 in the shared KGML.

| Test | Expected order | What I measured in the Python crop |
|---|---|---|
| One state | green | 650 green pixels |
| Two states | green, red | 316 green pixels on the left; 334 red on the right |
| Three states | green, gray, red | 212 green, 206 gray, and 232 red pixels in order |

The strongest competing color count was zero in each Python band. The R
comparison also passed its one-, two-, and three-state checks. The tiny crop
images are in `../results/python-pathview/figures/` and
`../results/r-pathview/` so the band order can be checked by eye.

One of the three strong test IDs, 1956, is not present in this particular
frozen pathway. Both the input count and mapped count are recorded. I did not
turn an unmapped ID into a fake success.

## Gene and compound data together

I tested hsa00020 with two gene states and two compound states.

- Pathview Plus mapped **3/3 gene IDs** onto 4 gene-node rows.
- It mapped **2/2 compound IDs** onto 2 compound-node rows.
- The native and vector figures were both written.
- C00022 stayed at the KGML location x=716, y=241.

The R baseline also mapped the controlled genes and compounds. One geometry
difference is worth reviewing: R's colored C00022 region measured as an
8-pixel radius, while Pathview Plus treats the KGML width and height of 8 as
the full diameter and uses a 4-pixel radius. This is a reproducible convention
difference, not a crash.

## SBGN checks inside Pathview Plus

For P00001, the bare and default-namespace files produced the same result:

- 76 primary glyphs plus 2 compartments
- 83 arcs
- 83/83 arcs resolved

For the smaller ports fixture, Pathview Plus resolved 3/3 arcs, including 2
arcs whose endpoints were ports. It also preserved the fixture's state
variable and clone marker.

For the two-condition gene-symbol table, Pathview Plus used all **7/7 input
symbols** and colored **9/28 gene-class glyph rows**. PNG, PDF, and SVG outputs
were all nonempty and valid. I compare these exact values with official R
SBGNview in `SBGNVIEW-COMPARISON-NOTES.md`.

## Other functions I covered

| Area | Evidence from my run |
|---|---|
| KEGG parsing | 115 hsa04110 nodes and 79 relation edges |
| Reaction parsing | The hsa00020 fixture supplied reaction-derived edges |
| Batch rendering | 2 valid pathways were kept and 1 missing ID was recorded separately |
| Highlighting | The modified image changed visibly; the original image stayed unchanged |
| Expansion | 115 original nodes became 170 after splitting groups and multi-gene nodes |
| Expanded edges | 638 edges remained connected to existing expanded node IDs |
| SBGN index | 5,206 entries across Reactome, SMPDB, PANTHER, MetaCyc, and MetaCrop |
| Offline ID route | Known Entrez IDs 1017 and 7157 resolved to CDK2 and TP53 |
| CLI | Version, species, rendering, SBGN rendering, and parity commands completed |

## A small beginner input issue I would clean up

A normal numeric Entrez column works. I did find one edge case with a completely
blank row: if a table contains a mapped ID, an unmatched ID, and an all-null
row, the Python call reaches a mixed `str`/`None` sort and raises a `TypeError`.
For now, the beginner-safe cleanup is:

```python
data = data.drop_nulls()
```

I saved the exact reproduction in `comparison.json` as `PY-OBS-001`. I would
consider dropping all-null rows inside the package so a blank spreadsheet line
does not surprise a new user.

## A small repository-documentation issue

The pinned README links to `BUG_CHECKLIST.md`, but that file is missing. It
also says 21 confirmed v3.0 bugs were fixed while the changelog says 18. I
saved the exact line-level check in `../results/documentation-check.txt`. This
is a documentation consistency issue, not a pathway runtime failure.

## How I interpreted the package's parity percentages

Pathview Plus contains its own 74-row feature matrix. That matrix says 73
features are full, with declared coverage of 97.0% versus R Pathview and 98.1%
versus R SBGNview. I exported it to
`../results/python-pathview/tables/project-declared-feature-matrix.csv`.

I label these as **project-declared feature percentages**, not as my independent
scientific equivalence score. My controlled R runs are the independent part of
this folder.

## Reproduce my Python run

From the repository root:

```bash
cd 08-11-2026
MPLBACKEND=Agg .venv/bin/python scripts/run_python_v3_comparison.py
```

Expected ending:

```text
16 passed, 0 failed
```

The run stays offline and does not change the Pathview Plus source checkout.
