# Setup and rerun instructions

The finished evidence is already saved. These steps are only needed if I want
to regenerate it.

## Python setup

From `08-11-2026`:

```bash
git clone https://github.com/raw-lab/pathview-plus sources/pathview-plus
git -C sources/pathview-plus checkout d4d45decec56e1ebec15cf04ae62ff944851780e

python3 -m venv .venv
.venv/bin/python -m pip install -e 'sources/pathview-plus[dev,layouts]'
.venv/bin/python -m pip install -r requirements-notebook.txt
```

## Run the independent Python comparison

```bash
MPLBACKEND=Agg .venv/bin/python scripts/run_python_v3_comparison.py
```

Expected ending:

```text
16 passed, 0 failed
```

## Run the Python SBGN comparison

```bash
MPLBACKEND=Agg .venv/bin/python scripts/run_python_sbgnview_comparison.py
```

## Run R Pathview

The R runner uses the project library in
`../pygage-pathview-validation/.r-library`.

```bash
R_LIBS_USER="$PWD/../pygage-pathview-validation/.r-library" \
  Rscript scripts/run_r_pathview_comparison.R
```

## Run R SBGNview

```bash
R_LIBS_USER="$PWD/../pygage-pathview-validation/.r-library" \
  Rscript scripts/run_sbgnview_comparison.R
```

The tested R environment contains:

- R 4.6.1
- Bioconductor 3.23
- Pathview 1.52.0
- SBGNview 1.26.0
- SBGNview.data 1.26.0
- rsvg 2.7.0

## Build and execute the notebook

```bash
.venv/bin/python scripts/build_and_run_notebook.py
```

The build is successful when `notebooks/execution-report.json` says:

```json
{
  "executed_code_cells": 11,
  "unexecuted_code_cells": 0,
  "error_outputs": 0,
  "status": "pass"
}
```

## Notes about internet use

The controlled comparisons use frozen local KEGG and SBGN files and run
offline. Internet access is only needed for the initial Git clone and package
installation. The three live SBGN download tests in the upstream suite remain
separately marked as skipped unless network testing is intentionally enabled.

