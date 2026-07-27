# Configure performance, threads, and data assets

*Page 27 of 31*

Use this page when an analysis will run on a shared computer, workstation, or
high-performance computing cluster.

The examples describe PyGAGE 1.2.1 from source commit `486e0b8`. They show how
to choose a predictable worker count, coordinate numerical libraries, locate
reference assets, record random settings, and reproduce the repository's
GAGE-R parity comparison.

## Begin with the safest setting

PyGAGE's analysis engine uses:

```python
n_jobs=1
```

by default. This runs the gene-set loop serially and is the best first run on a
laptop or shared login node.

A good performance workflow is:

```text
run with 1 worker
        |
        v
confirm the result and record the runtime
        |
        v
try the number of workers allocated to the job
        |
        v
compare runtime while keeping analysis settings unchanged
```

More workers change how work is scheduled. They do not change the intended
statistical method.

## Understand the different thread pools

Several layers may use threads:

| Layer | Control | Job |
| --- | --- | --- |
| PyGAGE gene-set loop | `n_jobs` | evaluates different gene sets |
| PyGAGE environment helper | `PYGAGE_NUM_THREADS` | supplies a value through `config.default_n_jobs()` |
| Polars | `POLARS_MAX_THREADS` | table operations |
| OpenMP | `OMP_NUM_THREADS` | numerical kernels using OpenMP |
| OpenBLAS | `OPENBLAS_NUM_THREADS` | linear-algebra operations using OpenBLAS |
| Intel MKL | `MKL_NUM_THREADS` | linear algebra using MKL |
| NumExpr | `NUMEXPR_NUM_THREADS` | NumExpr calculations |

Coordinating them prevents several libraries from independently assuming that
they may use the entire computer.

## Understand `n_jobs`

`GAGEAnalysis.run_gage()` has:

```python
n_jobs=1
```

The high-level `gage()` function accepts the same setting through its extra
keyword arguments:

```python
result = gage(
    prepared_data,
    gene_sets,
    prepared=True,
    n_jobs=2,
)
```

The implemented meanings are:

| Value | Behavior |
| ---: | --- |
| `1` | serial gene-set evaluation; the default |
| `0` | serial gene-set evaluation |
| positive value above `1` | a thread pool with that maximum worker count |
| negative value | Python selects its default thread-pool worker count |

PyGAGE documents `n_jobs=-1` as the all-available-cores shortcut. On a shared
system, an explicit positive number is more predictable because it can match
the number of CPUs assigned by the scheduler.

`n_jobs` parallelizes the main loop over gene sets. The chosen test, meta
method, set-size range, and input data remain separate settings.

## Use `PYGAGE_NUM_THREADS` deliberately

The helper:

```python
from pygage import config

jobs = config.default_n_jobs()
```

reads `PYGAGE_NUM_THREADS`.

Its behavior is:

| Environment value | Returned value |
| --- | ---: |
| variable not set | `1` |
| positive integer such as `4` | `4` |
| `0` or a negative integer | `1` |
| non-integer text | `1` |

Pass the result into the analysis explicitly:

```python
from pygage import config
from pygage.core import GAGEAnalysis


jobs = config.default_n_jobs()

result = GAGEAnalysis().run_gage(
    prepared_data,
    gene_sets,
    n_jobs=jobs,
)
```

`run_gage()` has a literal default of `1`; it does not read
`PYGAGE_NUM_THREADS` automatically. The explicit
`n_jobs=config.default_n_jobs()` connection makes the environment setting
active and visible in the script.

## Set thread variables before importing Polars

`POLARS_MAX_THREADS` sizes the Polars pool when Polars is first initialized.
Set it before importing Polars or PyGAGE.

This ordering is reliable:

```python
import os

os.environ["POLARS_MAX_THREADS"] = "2"

import polars as pl
import pygage
```

This ordering is too late to resize an already initialized Polars pool:

```python
import polars as pl

import os
os.environ["POLARS_MAX_THREADS"] = "2"
```

The simplest method is to set the variables in Terminal before starting
Python.

## macOS and Linux: conservative parallel profile

The following profile gives PyGAGE and Polars four workers while keeping each
BLAS/OpenMP pool at one thread. This helps avoid nested multiplication of
threads.

```bash
export PYGAGE_NUM_THREADS=4
export POLARS_MAX_THREADS=4
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

python reproducible_performance_run.py
```

These exports affect the current Terminal session and programs started from
it.

For the most conservative shared-computer run:

```bash
export PYGAGE_NUM_THREADS=1
export POLARS_MAX_THREADS=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

python reproducible_performance_run.py
```

## Windows PowerShell: conservative parallel profile

```powershell
$env:PYGAGE_NUM_THREADS = "4"
$env:POLARS_MAX_THREADS = "4"
$env:OMP_NUM_THREADS = "1"
$env:OPENBLAS_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"

python .\reproducible_performance_run.py
```

For a one-worker shared-computer run:

```powershell
$env:PYGAGE_NUM_THREADS = "1"
$env:POLARS_MAX_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:OPENBLAS_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"

python .\reproducible_performance_run.py
```

PowerShell environment settings apply to the current PowerShell session and
programs started from it.

## Use `config.set_thread_limits()`

PyGAGE provides:

```python
config.set_thread_limits(n_threads)
```

It sets all six controls to the same positive limit:

- `PYGAGE_NUM_THREADS`;
- `POLARS_MAX_THREADS`;
- `OMP_NUM_THREADS`;
- `OPENBLAS_NUM_THREADS`;
- `MKL_NUM_THREADS`; and
- `NUMEXPR_NUM_THREADS`.

It converts values below one to one.

Create `uniform_thread_limit.py`:

```python
import os


# Set the Polars variable before importing PyGAGE or Polars.
thread_limit = 2
os.environ["POLARS_MAX_THREADS"] = str(thread_limit)

from pygage import config


config.set_thread_limits(thread_limit)

print("Default PyGAGE jobs:", config.default_n_jobs())
print("Active thread report:", config.thread_config())
```

Run:

```bash
python uniform_thread_limit.py
```

Call `set_thread_limits()` before the first Polars table operation. Setting
`POLARS_MAX_THREADS` in the shell or at the very top of the file also ensures
that the Polars pool is initialized at the intended size.

`set_thread_limits()` is convenient when one uniform ceiling is desired. The
conservative profiles above set PyGAGE/Polars separately from BLAS so several
gene-set workers do not each request several BLAS workers.

## Inspect the active configuration

Use:

```python
from pygage import config


print(config.thread_config())
```

The returned dictionary reports:

```text
PYGAGE_NUM_THREADS
POLARS_MAX_THREADS
OMP_NUM_THREADS
polars_pool_size
```

Record the other coordinated environment variables directly:

```python
import os


for name in (
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    print(name, os.environ.get(name))
```

## Safe use on a scheduler

Use the worker count granted to the job, not the total CPUs installed on the
shared node.

A SLURM submission file named `run_pygage.slurm` can contain:

```bash
#!/usr/bin/env bash
#SBATCH --job-name=pygage
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=pygage-%j.log

set -euo pipefail

THREADS="${SLURM_CPUS_PER_TASK:-1}"

export PYGAGE_NUM_THREADS="$THREADS"
export POLARS_MAX_THREADS="$THREADS"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

source .venv/bin/activate
python reproducible_performance_run.py
```

Submit it with:

```bash
sbatch run_pygage.slurm
```

On another scheduler, use its equivalent allocated-CPU variable. Ask for the
memory and time appropriate to the dataset. Avoid running a multi-worker
analysis directly on a shared login node.

## Complete reproducible performance script

This example uses the real prepared GSE16873 data and KEGG gene sets bundled
with PyGAGE. It requires no database download.

Create `reproducible_performance_run.py`:

```python
import os


# Set pool sizes before importing PyGAGE, Polars, NumPy, or SciPy.
try:
    n_jobs = max(
        1,
        int(os.environ.get("PYGAGE_NUM_THREADS", "1")),
    )
except ValueError:
    n_jobs = 1

os.environ["PYGAGE_NUM_THREADS"] = str(n_jobs)
os.environ.setdefault("POLARS_MAX_THREADS", str(n_jobs))
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import hashlib
import json
import platform
from pathlib import Path

import polars as pl
import pygage
from pygage import config
from pygage.core import GAGEAnalysis


SOURCE_COMMIT = "486e0b8"
PERMUTATIONS = 100
RANDOM_STATE = 20260727


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# Locate the regression assets bundled inside the installed package.
regression_folder = (
    config.packaged_data_dir()
    / "regression"
)
matrix_file = regression_folder / "gse16873_prepared.csv.gz"
gene_set_file = regression_folder / "kegg_gs.json"

prepared = pl.read_csv(
    matrix_file,
    schema_overrides={"gene_id": pl.Utf8},
)
gene_sets = json.loads(
    gene_set_file.read_text(encoding="utf-8")
)

# Connect PYGAGE_NUM_THREADS to the engine explicitly.
n_jobs = config.default_n_jobs()

results = GAGEAnalysis().run_gage(
    expression_data=prepared,
    gene_sets=gene_sets,
    gene_col="gene_id",
    set_size_range=(10, 500),
    same_dir=True,
    test_method="t-test",
    meta_method="stouffer",
    fdr_method="BH",
    compute_effect=True,
    leading_edge=False,
    permutations=PERMUTATIONS,
    n_jobs=n_jobs,
    random_state=RANDOM_STATE,
)

output_folder = Path("reproducible_performance_output")
output_folder.mkdir(exist_ok=True)

results["greater"].write_csv(
    output_folder / "greater.csv"
)
results["less"].write_csv(
    output_folder / "less.csv"
)
results["stats"].write_csv(
    output_folder / "stats.csv"
)

pool_environment = {
    name: os.environ.get(name)
    for name in (
        "PYGAGE_NUM_THREADS",
        "POLARS_MAX_THREADS",
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    )
}

provenance = {
    "pygage_version": pygage.__version__,
    "pygage_source_commit": SOURCE_COMMIT,
    "python_version": platform.python_version(),
    "matrix_file": str(matrix_file),
    "matrix_sha256": sha256_file(matrix_file),
    "gene_set_file": str(gene_set_file),
    "gene_set_sha256": sha256_file(gene_set_file),
    "matrix_shape": list(prepared.shape),
    "gene_set_count": len(gene_sets),
    "test_method": "t-test",
    "meta_method": "stouffer",
    "fdr_method": "BH",
    "set_size_range": [10, 500],
    "permutations": PERMUTATIONS,
    "random_state": RANDOM_STATE,
    "n_jobs": n_jobs,
    "thread_config": config.thread_config(),
    "pool_environment": pool_environment,
}

(output_folder / "provenance.json").write_text(
    json.dumps(provenance, indent=2),
    encoding="utf-8",
)

print("PyGAGE version:", pygage.__version__)
print("Prepared shape:", prepared.shape)
print("Gene sets:", len(gene_sets))
print("n_jobs:", n_jobs)
print("Thread configuration:", config.thread_config())
print("Saved:", output_folder)
```

Run with the one-worker or multi-worker environment commands shown above:

```bash
python reproducible_performance_run.py
```

The output folder contains:

```text
reproducible_performance_output/
├── greater.csv
├── less.csv
├── stats.csv
└── provenance.json
```

## Reproduce permutation results

Permutation p-values are requested with:

```python
permutations=100
```

and controlled with:

```python
random_state=20260727
```

`random_state` seeds PyGAGE's NumPy random generator for the permutation null.
Use the same:

- input files;
- gene sets;
- preprocessing;
- permutation count;
- random state;
- PyGAGE version; and
- analysis settings

to reproduce the permutation result.

Analytic p-values do not require permutations. Increasing `permutations`
increases the additional work, so begin with a small teaching count and choose
the final count in the analysis plan.

## Understand data-asset resolution

PyGAGE contains a small packaged data directory. It includes the default
Entrez-to-symbol mapping and regression fixtures.

The asset resolution order is:

```text
explicit file path
        |
        v
matching file in PYGAGE_DATA_DIR
        |
        v
file bundled with the installed package
```

### Configuration functions

| Function | Return |
| --- | --- |
| `config.packaged_data_dir()` | installed package's `data` directory |
| `config.data_dir()` | valid `PYGAGE_DATA_DIR`, otherwise packaged directory |
| `config.resolve(name, explicit=None)` | resolved path for one named asset |
| `config.egsymb_path(explicit=None)` | resolved path for `egSymb.tsv` |
| `config.ensure_egsymb(explicit=None, fetch=False, species="hsa")` | usable Entrez-symbol mapping path |

Inspect the paths:

```python
from pygage import config


print("Packaged data:", config.packaged_data_dir())
print("Active data:", config.data_dir())
print("Resolved map:", config.resolve("egSymb.tsv"))
print("Entrez-symbol map:", config.egsymb_path())
```

`resolve()` uses an explicit path immediately when one is provided. Without an
explicit path, it uses the named file inside `PYGAGE_DATA_DIR` when that file
exists, then uses the packaged file.

## Set `PYGAGE_DATA_DIR` on macOS or Linux

Create a project reference-data folder:

```bash
mkdir -p reference_data
export PYGAGE_DATA_DIR="$PWD/reference_data"

python -c "from pygage import config; print(config.data_dir())"
```

Place a curated mapping at:

```text
reference_data/egSymb.tsv
```

PyGAGE then resolves that file before the packaged mapping.

## Set `PYGAGE_DATA_DIR` on Windows PowerShell

```powershell
New-Item -ItemType Directory -Force reference_data | Out-Null
$env:PYGAGE_DATA_DIR = Join-Path (Get-Location) "reference_data"

python -c "from pygage import config; print(config.data_dir())"
```

Place the curated mapping at:

```text
reference_data\egSymb.tsv
```

## Use the packaged or refreshed Entrez-symbol map

Use the available local map:

```python
from pygage import config


mapping_path = config.ensure_egsymb()
print(mapping_path)
```

This is the default:

```python
fetch=False
```

To request a refreshed map for a KEGG organism:

```python
from pygage import config


mapping_path = config.ensure_egsymb(
    fetch=True,
    species="hsa",
)
print(mapping_path)
```

`fetch=True` contacts the KEGG REST service, builds an Entrez-symbol map, and
saves `egSymb.tsv` in the active data directory. The packaged map remains the
local fallback.

To use one explicitly named file:

```python
from pygage import config


mapping_path = config.ensure_egsymb(
    explicit="reference_data/my_egSymb.tsv",
    fetch=False,
)
print(mapping_path)
```

Record whether the mapping was packaged, supplied through
`PYGAGE_DATA_DIR`, given explicitly, or refreshed from KEGG.

## Reproduce the repository parity workflow

The PyGAGE repository contains three scripts under `results/`:

| Script | Role |
| --- | --- |
| `01_setup.sh` | prepares R/gage and checks Python comparison dependencies |
| `02_run_gage_reference.R` | runs the GAGE R reference and exports common inputs and results |
| `03_compare.py` | runs PyGAGE on the identical prepared input and compares columns |

The comparison uses the GAGE demonstration dataset:

- 11,979 genes;
- six HN reference samples;
- six DCIS sample columns;
- a paired comparison; and
- the same prepared matrix and KEGG set membership for both implementations.

### macOS or Linux

Start in a working folder:

```bash
git clone https://github.com/raw-lab/pygage.git
cd pygage
git checkout 486e0b8

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

Rscript --version

cd results
bash 01_setup.sh
Rscript 02_run_gage_reference.R
python 03_compare.py --gage-out gage_out --tol 1e-8
```

On Debian or Ubuntu, `01_setup.sh` can install `r-base-core` when `Rscript` is
not present. On macOS, install R first and confirm `Rscript --version`; the
script then prepares the remaining reference environment.

### Windows PowerShell

Install R, place `Rscript` on `PATH`, and then run:

```powershell
git clone https://github.com/raw-lab/pygage.git
Set-Location pygage
git checkout 486e0b8

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .

Rscript --version
Rscript -e "if (!requireNamespace('BiocManager', quietly=TRUE)) install.packages('BiocManager', repos='https://cloud.r-project.org'); BiocManager::install('gage', update=FALSE, ask=FALSE)"

Set-Location results
Rscript .\02_run_gage_reference.R
python .\03_compare.py --gage-out gage_out --tol 1e-8
```

`01_setup.sh` is a Bash setup script. It can also be run on Windows through
Git Bash or Windows Subsystem for Linux:

```bash
cd pygage/results
bash 01_setup.sh
```

The PowerShell commands above perform the native Windows setup needed before
running scripts 02 and 03.

### What script 02 creates

`02_run_gage_reference.R` creates `results/gage_out/` containing:

```text
prepared_matrix.csv
kegg_gs.json
gage_tTest_greater.csv
gage_tTest_less.csv
gage_zTest_greater.csv
gage_fisher_greater.csv
```

It runs:

- the default t-test with Stouffer combination;
- the z-test with Stouffer combination; and
- the t-test with Fisher/gamma combination.

### What script 03 checks

`03_compare.py` reads that prepared matrix and those exact gene sets. It
compares:

- t-test greater results;
- t-test less results;
- z-test greater results; and
- Fisher greater results.

Depending on the result type, it checks `stat_mean`, `p_val`, `p_geomean`,
`q_val`, and `set_size` against the corresponding GAGE-R columns. The default
tolerance is:

```text
1e-8
```

It prints the maximum absolute difference, prints the leading twelve pathways,
reports Pearson correlations, and writes:

```text
results/pygage_vs_gageR.png
```

The repository also contains the archived reference folder
`results/gage_out_jul1626`. It can be checked directly:

```bash
cd results
python 03_compare.py \
  --gage-out gage_out_jul1626 \
  --tol 1e-8
```

During validation of this guide, that command compared 160 size-passing sets
and reported:

| Comparison | Maximum absolute difference |
| --- | ---: |
| t-test greater | `4.88e-15` |
| t-test less | `4.88e-15` |
| z-test greater | `5.77e-15` |
| Fisher greater | `1.67e-15` |

Both reported Pearson correlations were `1.00000000`, and all comparisons
passed the `1e-8` tolerance.

## Performance and provenance checklist

Save these details with every production run:

- PyGAGE version `1.2.1`;
- source commit `486e0b8`;
- Python version and operating system;
- input filenames and file checksums;
- gene-set source, release, identifier system, and checksum;
- `n_jobs`;
- `PYGAGE_NUM_THREADS`;
- `POLARS_MAX_THREADS`;
- `OMP_NUM_THREADS`;
- `OPENBLAS_NUM_THREADS`;
- `MKL_NUM_THREADS`;
- `NUMEXPR_NUM_THREADS`;
- scheduler CPU, memory, and time allocation;
- test, meta method, set-size range, and FDR method;
- permutation count and `random_state`;
- active `PYGAGE_DATA_DIR`;
- Entrez-symbol map source and retrieval date; and
- the exact script or command used.

## Final safety checklist

- thread variables are set before importing Polars or PyGAGE;
- `n_jobs` does not exceed the allocated worker count;
- BLAS/OpenMP pools are coordinated with PyGAGE workers;
- a one-worker result was checked before scaling;
- random state and permutation count are recorded;
- data assets resolve to the intended directory;
- packaged or refreshed mapping provenance is saved; and
- the parity workflow passes at the selected tolerance.

[<- Previous: Follow a real-data workflow](26-real-dataset.md) | [Home](index.md) | [Next: Recipe book ->](28-recipe-book.md)
