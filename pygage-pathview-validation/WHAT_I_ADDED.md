# What was added

Everything below is inside this validation folder. No PyGAGE or Pathview Plus source code was modified.

## Executed Jupyter notebooks

- `notebooks/00_START_HERE.ipynb`
- `notebooks/01_pygage_full_validation.ipynb`
- `notebooks/02_pathview_plus_full_validation.ipynb`
- `notebooks/03_r_vs_python_pathview.ipynb`

All code cells were executed in fresh kernels and contain no saved error outputs.

## Automated tests

- `tests/test_pygage_offline.py`
- `tests/test_pathview_offline.py`
- `tests/conftest.py`
- `pytest.ini`

The suite covers PyGAGE inputs, statistics, gene-set sources, results, plots, and R regression; plus Pathview one/two/three-state coloring, PNG/SVG geometry, compounds, parsing, aggregation, highlighting, and spline helpers.

## Reproducible scripts

- `scripts/run_pygage_validation.py`
- `scripts/run_pathview_validation.py`
- `scripts/run_r_pathview.R`
- `scripts/compare_r_python.py`
- `scripts/run_all.py`
- `scripts/build_notebooks.py`
- `scripts/validate_notebooks.py`
- `scripts/build_report.py`

## Input fixtures

- Beginner toy expression data and gene sets
- Single-state, half-and-half, and three-state Cell Cycle input
- Prepared PI3K–Akt, MAPK, gene-plus-compound, and KO nitrogen-metabolism inputs
- A project-local copy of the newest PyGAGE repository data and its regression fixtures
- The official frozen `hsa04110` KGML/PNG is copied from installed R pathview at run time

## Results and reports

- PyGAGE tables and charts in `results/pygage/`
- Python Pathview images/tables in `results/pathview_python/`
- R pathview images/tables in `results/pathview_r/`
- Direct comparison evidence in `results/comparison/`
- Full conclusion in `reports/FULL_VALIDATION_REPORT.md`
- Feature-by-feature coverage in `reports/FEATURE_MATRIX.csv`
- Machine-readable results in `reports/test_results.json`

## Environment files

- `requirements-validation.txt`
- `ENVIRONMENT.md`
- `.gitignore`

