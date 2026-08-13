# Pathview Plus bug checks

These are the Pathview Plus checks I worked on the night of
**August 10, 2026**. I made this folder because I wanted to actually run the
software and try everything I could, not just read through the documentation.
I also wanted my notes, tests, and example images in one place so someone else
in the lab could follow what I did.

I used the Python
[`raw-lab/pathview-plus`](https://github.com/raw-lab/pathview-plus) repository at
commit `07aee813375347bcc933ad21b4aed561dd7cd3bf`. That is the exact version I had
on my computer that night. None of these checks changes the Pathview Plus code.

## How I did the testing

I started with the basics, like someone trying Pathview Plus for the first time.
I checked whether it imported correctly and whether I could make a basic
pathway image. Then I kept changing one thing at a time. I added more gene
conditions, tried compounds, changed the colors, left some values blank, used
duplicate IDs, and tried files that were incomplete or formatted differently.

Whenever something looked off, I made a smaller example and ran it again. That
helped me tell the difference between a one-time weird result and something I
could reproduce. I turned those smaller examples into `pytest` tests so I could
run them again without retyping everything. For checks that used the same steps
with different inputs, I gave one test several values instead of making a new
copy of the test every time.

For the main image check, I used the official KEGG cell-cycle pathway
`hsa04110`. I saved the pathway files and used the same copy for each test. I
made a normal one-condition image, a half-and-half image, and an image with
three conditions. I opened the images after they were made and checked the
colors and the left-to-right order myself.

After I had the separate tests working, I wrote
[`scripts/run_deep_checks.py`](scripts/run_deep_checks.py) to run them together
and save the results. I used
[`scripts/generate_evidence.py`](scripts/generate_evidence.py) for the example
images and [`scripts/build_notebook.py`](scripts/build_notebook.py) for the
Jupyter notebook. The JSON, CSV, Markdown, and notebook files in this folder all
come from the same test run, so I did not have to copy the totals into each file
by hand.

Before I called it a night, I ran the whole thing again from the start. I
opened the notebook, checked the main images, and made sure the totals in the
different reports matched. The final run had **239 test cases**: **143 passed**,
**89 reproduced something that needs another look**, and **7 involved features
that were not fully connected yet**. There were **0 unexplained failures**.
Some findings were checked in more than one way, so those 89 test cases came
from **79 different findings**.

I left everything in this folder so we can run the same checks after the next
Pathview Plus update and compare the results.

## Where to start

There are a lot of files here, so I would start with these:

1. [`PATHVIEW-BUG-CHECKS.md`](PATHVIEW-BUG-CHECKS.md) is the easiest version of
   the results to read.
2. [`pathview_deep_bug_checks.executed.ipynb`](pathview_deep_bug_checks.executed.ipynb)
   shows the results and saved images in Jupyter.
3. [`TECHNICAL-FINDINGS.md`](TECHNICAL-FINDINGS.md) has the source locations and
   more detail for someone working on the code.
4. [`FEATURE-TEST-MATRIX.csv`](FEATURE-TEST-MATRIX.csv) and
   [`BUGS.json`](BUGS.json) have the complete results in formats that can be
   searched or loaded into another program.

## What I checked

I tried to cover both the usual Pathview Plus workflow and the kinds of inputs
that might behave differently. The checks include:

- installation, imports, versions, and all public exports;
- the main `pathview()` workflow with cached KEGG files;
- single-condition, left/right two-condition, and three-condition nodes;
- gene and compound mapping, duplicate IDs, nulls, aggregation methods, and
  `map_null` behavior;
- numeric color mapping, clipping, transformations, bins, invalid inputs, and
  discrete settings;
- KGML and SBGN parsing, including namespaces and malformed XML;
- native PNG, SVG, and graph/PDF output;
- node and edge highlighting, label changes, opacity, and file saving;
- Bezier, Catmull-Rom, and routing helpers;
- command-line behavior, including gene-only and compound-only inputs;
- KEGG, MyGene.info, Reactome, MetaCyc, PANTHER, and SMPDB integration code;
- repeatability, output dimensions, and basic performance.

The regular test run stays offline and uses saved examples. I put the live
website checks in a separate report because a website can change or go down
even when nothing in Pathview Plus has changed.

## How to run everything again

From the `PATHVIEW-MARKDOWN` folder, run:

```bash
cd "pathveiw bug checks"
../pygage-pathview-validation/.venv/bin/python scripts/run_deep_checks.py
```

This command updates the files in `results/`. It only exits as a failed run if
something new or unexplained happens. Findings that the tests are meant to
reproduce are saved as `KNOWN_BUG` so they stay visible in the report.

To run only the tests without rebuilding all of the evidence:

```bash
cd "pathveiw bug checks"
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/pathview-mpl \
  ../pygage-pathview-validation/.venv/bin/python -m pytest -c pytest.ini tests -ra
```

## What the labels mean

| Label | Meaning |
|---|---|
| `PASS` | The thing I tested worked. |
| `KNOWN_BUG` | I could repeat the same unexpected behavior with a focused test. |
| `FEATURE_GAP` | A feature is mentioned or partly present, but it is not fully connected yet. |
| `EXTERNAL` | The result depends on a live website and should be checked again later. |
| `NOT_RUN` | I intentionally left the test out of the regular offline run. |

## What these checks do not prove

I tested a lot of software behavior, but I did not test every biological
dataset that could possibly be used with Pathview Plus. These checks use small
controlled examples and one saved official KEGG pathway. Someone with the right
biology background still needs to review the biological meaning of a real
analysis.
