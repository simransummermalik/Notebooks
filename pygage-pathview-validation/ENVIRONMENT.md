# Validation environment

The delivered notebooks were executed on August 10, 2026 with:

- macOS on Apple silicon
- Python 3.14.3
- PyGAGE 1.2.1 from commit `265ab1a07a3987eba41779931053fbe7b3ef4fd3`
- Pathview Plus distribution 2.0.2 from commit `07aee813375347bcc933ad21b4aed561dd7cd3bf`
- R 4.6.1
- Bioconductor 3.23
- R pathview 1.52.0

## Recreate the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-validation.txt
```

## Install R pathview into the project-local library

```bash
mkdir -p .r-library
R_LIBS_USER="$PWD/.r-library" Rscript -e \
  'install.packages("BiocManager", repos="https://cloud.r-project.org"); BiocManager::install("pathview", ask=FALSE, update=FALSE)'
```

## Start Jupyter

```bash
source .venv/bin/activate
jupyter lab
```

Open `notebooks/00_START_HERE.ipynb` first.

