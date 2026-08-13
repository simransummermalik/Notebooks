# PyGAGE and Pathview validation

This folder is a reproducible, local test package for the current versions of:

- **PyGAGE** (`raw-lab/pygage`)
- **Pathview Plus for Python** (`raw-lab/pathview-plus`)
- **pathview for R** (Bioconductor)

It answers four practical questions:

1. Does PyGAGE run the major documented analysis, input, gene-set, result, plotting, and command-line workflows?
2. Does Pathview Plus run the major documented KEGG mapping and rendering workflows?
3. Does a one-condition pathway produce the normal single-color node view?
4. Does a two-condition pathway split each mapped node into a **left half and a right half**, in the same condition order used by R pathview's `multi.state = TRUE`?

Nothing in this folder is automatically published. Running the notebooks or tests only creates files on this computer.

## Start with the Jupyter notebook

Open this first:

```text
notebooks/00_START_HERE.ipynb
```

It links to the three detailed notebooks:

1. `notebooks/01_pygage_full_validation.ipynb`
2. `notebooks/02_pathview_plus_full_validation.ipynb`
3. `notebooks/03_r_vs_python_pathview.ipynb`

Each notebook starts with a beginner explanation, runs real code, saves its outputs, and ends with plain-English checks. All four delivered notebooks have already been executed from top to bottom with no cell errors.

## Run everything from Terminal

From this folder:

```bash
source .venv/bin/activate
export MPLBACKEND=Agg
export MPLCONFIGDIR="$PWD/.mplconfig"
python scripts/run_all.py
```

The summary is written to `reports/FULL_VALIDATION_REPORT.md`. Machine-readable results are written to `reports/test_results.json` and `reports/FEATURE_MATRIX.csv`.

Add `--live` when fresh KEGG access is available:

```bash
python scripts/run_all.py --live
```

Add `--execute-notebooks` if you also want to overwrite the notebooks with newly executed outputs:

```bash
python scripts/run_all.py --execute-notebooks
```

## Run only the automated Python tests

```bash
source .venv/bin/activate
MPLBACKEND=Agg MPLCONFIGDIR="$PWD/.mplconfig" pytest -q
```

Offline tests do not require KEGG access. Integration tests download current KEGG pathway files and therefore require an internet connection.

## Current completed result

- Offline assertions: 41 passed, 8 expected compatibility findings, 0 unexpected failures.
- PyGAGE workflows: 5 passed; the new pathway gene-color chart has a Matplotlib 3.11 compatibility finding.
- Python Pathview reproducible workflows: 7 passed, 0 failed; 5 fresh live-service cases were not run.
- R pathview workflows: 7 passed, 0 failed.
- R/Python mapped values and half-and-half pixel orientation: passed.

## Important wording

The two-condition example is called a **multi-state pathway**. With exactly two columns, the first column colors the left half and the second column colors the right half. This is different from R pathview's Graphviz-only `split.group` option.
