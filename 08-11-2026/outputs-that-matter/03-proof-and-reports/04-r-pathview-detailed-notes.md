# R Pathview Comparison Notes — August 11, 2026

## Bottom line

I ran an offline, controlled R Pathview baseline so we can compare it with Pathview Plus v3 using the same pathway files and known values. I got **10 passes, 1 reproducible comparison failure, and 0 skipped checks**.

R Pathview completed every requested workflow: one state, two-state half-and-half, three states, the shared Control/Treatment dataset, a native PNG, a Graphviz PDF, and a pathway with both gene and compound data. The one failed check is a real geometry difference, not a crash: R Pathview draws a compound with an observed radius of 8 pixels when the KGML width and height are 8 pixels. Pathview Plus v3 treats those dimensions as the full diameter and uses a 4-pixel radius.

The machine-readable evidence is in `../results/r-pathview/comparison.json`, and the flat check table is in `../results/r-pathview/check-results.csv`.

## Exact environment

| Component | Version or identifier |
|---|---|
| R | 4.6.1 (2026-06-24) |
| Platform | aarch64-apple-darwin25.4.0 |
| R Pathview | 1.52.0 |
| Bioconductor | 3.23 |
| Rgraphviz | 2.56.0 |
| Pathview Plus comparison version | 3.1.0 |
| Pathview Plus comparison commit | `d4d45decec56e1ebec15cf04ae62ff944851780e` |

I reused `pygage-pathview-validation/.r-library` without installing into or changing that library. The script copied the frozen fixtures into the August 11 results folder before rendering. It did not use the network or modify the checked-out source repositories.

## Check-by-check result

| ID | Check | Status | Main evidence |
|---|---|---|---|
| R01 | Environment and package versions | PASS | R Pathview 1.52.0 and Pathview Plus 3.1.0 at the pinned commit were identified. |
| R02 | Frozen offline hsa04110 fixture | PASS | The input image is 1039 × 801 pixels; XML and PNG hashes are recorded in JSON. |
| R03 | One-state native pathway | PASS | Three controlled gene nodes mapped and a 1039 × 801 PNG was written. |
| R04 | Two-state half-and-half pathway | PASS | CDKN2A was green on the left and red on the right. |
| R05 | Shared Control/Treatment dataset | PASS | All five requested Entrez IDs mapped to the frozen hsa04110 pathway. |
| R06 | Three-state native pathway | PASS | CDKN2A rendered green, gray, and red from left to right. |
| R07 | Native dimensions and gene geometry | PASS | All native outputs stayed 1039 × 801; CDKN2A stayed at x=532, y=124, width=46, height=17. |
| R08 | Two-state Graphviz pathway | PASS | A 19,039-byte file with a `%PDF` signature was written. |
| R09 | Gene and compound data together | PASS | Four gene rows and two compound rows mapped on the controlled hsa00020 test. |
| R10 | Native compound center orientation | PASS | C00022 stayed near x=716, y=241 instead of being vertically mirrored. |
| R11 | Compound size parity with v3 | **FAIL** | R radius was 8 pixels; the KGML-diameter/v3 expectation was 4 pixels. |

Here, **FAIL** means the measured R result differed from the Pathview Plus v3 convention. It does not mean that R Pathview stopped running.

## Shared notebook dataset

I added the exact shared dataset requested for the R-versus-Python notebook:

| Entrez ID | Control | Treatment |
|---:|---:|---:|
| 1017 | -1.5 | 1.5 |
| 1019 | -0.7 | 0.7 |
| 1021 | 0.0 | 0.0 |
| 595 | 0.8 | -0.8 |
| 7157 | 1.4 | -1.4 |

The exact input is saved as `../results/r-pathview/shared-hsa04110-control-treatment-input.csv`. The output is `../results/r-pathview/hsa04110.r-shared-control-treatment.multi.png`, where Control is the left half and Treatment is the right half.

All five IDs were present in the frozen KGML. IDs 1019 and 1021 share one KEGG node, so R Pathview reports their node-level aggregate on that row. Because 1021 is zero in both states, that displayed row stays at -0.7 and 0.7. ID 1017 appears at two pathway locations, so it produces two selected node rows. The exact selected rows and colors are in `../results/r-pathview/hsa04110.r-shared-control-treatment.selected-nodes.csv`.

## Native rendering evidence

For the original two-state half-and-half test, I used CDKN2A/Entrez 1029 with Classical=-2 and Basal=+2. Its KGML node was x=532, y=124, width=46, height=17. In the saved crop I counted:

- Left half: 303 green pixels and 0 red pixels.
- Right half: 334 red pixels and 13 green pixels.

The small number of green pixels counted on the right comes from the shared boundary/anti-aliasing area of the raster crop. The dominant color and state order are clear in the saved counts.

For the three-state test, the same node used -2, 0, and +2. The dominant counts were 199 green pixels in the left third, 180 gray pixels in the middle third, and 232 red pixels in the right third.

The source image and all one-, two-, and three-state native results remained exactly 1039 × 801 pixels.

## Gene and compound behavior

The local v3 repository has a frozen hsa00020 KGML with both genes and compounds but no matching native PNG. To keep this test offline and make the pixel geometry measurable, I placed that KGML over a locally generated 1000 × 800 white PNG.

R Pathview successfully mapped:

- Genes 1738, 1743, and 1737 across Low and High states.
- Compounds C00022 and C00122 across Low and High states.

C00022 is centered at x=716, y=241 in the KGML. Its measured colored center was x=717, y=242, within one raster pixel. The vertically mirrored candidate would have been y=559, so the R native result clearly used the top-left image coordinate convention.

The colored compound bounding box ran from x=710 to 724 and y=235 to 249. This gives an observed half-width and half-height of 8 pixels. The KGML says width=8 and height=8, so a diameter interpretation gives a 4-pixel radius. That is the one reproducible R-versus-v3 geometry difference I found.

## Warning seen in the controlled compound test

The blank-background gene/compound test produced this warning 132 times:

```text
number of rows of result is not a multiple of vector length (arg 2)
```

I traced it to R Pathview's native gene renderer at `render.kegg.node()` when it calls `cbind(blk.ind, j)`. The blank test image does not contain the black node-border pixels that the renderer normally expects, so `blk.ind` can be empty. The render still completed and the controlled gene and compound values were mapped correctly.

I would not report this as a general Pathview bug from this test alone. I would first repeat it with the official hsa00020 KEGG background. I preserved the exact warning and count in `comparison.json` so it is not hidden.

## Main output files

- `hsa04110.r-one-state.png` — one gene state.
- `hsa04110.r-half-half.multi.png` — strong low/high half-and-half control.
- `hsa04110.r-shared-control-treatment.multi.png` — exact shared notebook dataset.
- `hsa04110.r-three-state.multi.png` — three ordered states.
- `hsa04110.r-graph.multi.pdf` — two-state Graphviz output.
- `hsa00020.r-gene-compound.multi.png` — combined gene and compound test.
- `compound-geometry.json` — measured compound geometry.
- `comparison.json` — complete versions, assertions, warnings, hashes, sizes, and results.
- `check-results.csv` — one row per check.

All of these files are under `08-11-2026/results/r-pathview/`.

## Reproduce it

From the repository root, I used:

```bash
R_LIBS_USER="$PWD/pygage-pathview-validation/.r-library" \
  Rscript 08-11-2026/scripts/run_r_pathview_comparison.R
```

The run is deterministic and offline as long as the existing R library and frozen source fixtures remain available. I did not change anything in the August 10 folder.
