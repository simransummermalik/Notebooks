# Use pandas or AnnData

*Page 14 of 31*

PyGAGE 1.2.1 accepts tables already held in pandas and expression matrices held
in AnnData. The high-level `gage()` function converts them at the input
boundary and returns Polars result tables.

## Complete pandas example

Create `run_pandas.py`:

```python
import pandas as pd
import polars as pl
from pygage import gage


expression = pd.DataFrame(
    {
        "gene_id": [
            "1", "2", "3", "4", "5", "6",
            "7", "8", "9", "10", "11", "12",
        ],
        "reference_1": [
            6.0, 7.0, 5.5, 6.5, 4.5, 5.0,
            7.0, 6.5, 5.5, 6.0, 4.8, 5.2,
        ],
        "reference_2": [
            6.2, 6.8, 5.7, 6.3, 4.7, 5.1,
            6.8, 6.6, 5.4, 6.1, 4.9, 5.3,
        ],
        "treatment_1": [
            8.4, 9.0, 7.3, 8.0, 4.3, 5.1,
            5.2, 4.4, 4.0, 4.8, 5.1, 5.1,
        ],
        "treatment_2": [
            8.4, 8.7, 7.3, 7.7, 4.7, 5.3,
            5.1, 4.7, 4.0, 5.0, 5.1, 5.3,
        ],
    }
)

gene_sets = {
    "Growth pathway": ["1", "2", "3", "4"],
    "Stress pathway": ["7", "8", "9", "10"],
    "Mixed pathway": ["3", "5", "8", "11"],
}

results = gage(
    data=expression,
    gene_sets=gene_sets,
    ref_indices=[0, 1],
    samp_indices=[2, 3],
    gene_col="gene_id",
    comparison="paired",
    input_logged=True,
    set_size_range=(2, 10),
)

print("Returned type:", type(results))
print(results)

greater = results.filter(
    pl.col("direction") == "greater"
)
greater.write_csv("pandas_greater.csv")
```

Run:

```bash
python run_pandas.py
```

The input is pandas, but `results` is a Polars DataFrame. Use Polars expressions
such as `pl.col(...)` for result filtering.

## pandas table rules

- Keep gene IDs in an explicit named column for the clearest workflow.
- Rows are genes and numeric columns are samples or prepared values.
- With a raw sample matrix, provide reference and sample indices.
- With a prepared table, use `prepared=True`.
- The gene column is converted to text.

## Install AnnData support

AnnData is optional. With the guide environment active:

```bash
python -m pip install anndata
```

## AnnData orientation

An AnnData expression matrix uses:

```text
observations x variables
samples      x genes
```

PyGAGE converts it to:

```text
genes x samples
```

It uses:

- `adata.var_names` for gene IDs;
- `adata.obs_names` for sample names; and
- `adata.X` for measurements.

## Complete AnnData example

Create `run_anndata.py`:

```python
import anndata as ad
import numpy as np
import polars as pl
from pygage import gage


genes = [
    "1", "2", "3", "4", "5", "6",
    "7", "8", "9", "10", "11", "12",
]
samples = [
    "reference_1",
    "reference_2",
    "treatment_1",
    "treatment_2",
]

# Rows in this temporary array are genes; columns are samples.
gene_by_sample = np.array(
    [
        [6.0, 6.2, 8.4, 8.4],
        [7.0, 6.8, 9.0, 8.7],
        [5.5, 5.7, 7.3, 7.3],
        [6.5, 6.3, 8.0, 7.7],
        [4.5, 4.7, 4.3, 4.7],
        [5.0, 5.1, 5.1, 5.3],
        [7.0, 6.8, 5.2, 5.1],
        [6.5, 6.6, 4.4, 4.7],
        [5.5, 5.4, 4.0, 4.0],
        [6.0, 6.1, 4.8, 5.0],
        [4.8, 4.9, 5.1, 5.1],
        [5.2, 5.3, 5.1, 5.3],
    ],
    dtype=float,
)

# AnnData stores samples x genes, so transpose the array.
adata = ad.AnnData(X=gene_by_sample.T)
adata.obs_names = samples
adata.var_names = genes

gene_sets = {
    "Growth pathway": ["1", "2", "3", "4"],
    "Stress pathway": ["7", "8", "9", "10"],
    "Mixed pathway": ["3", "5", "8", "11"],
}

results = gage(
    data=adata,
    gene_sets=gene_sets,
    ref_indices=[0, 1],
    samp_indices=[2, 3],
    comparison="paired",
    input_logged=True,
    set_size_range=(2, 10),
)

print(results)
results.write_csv("anndata_results.csv")

print(
    "Top greater:",
    results
    .filter(pl.col("direction") == "greater")
    .head(1),
)
```

Run:

```bash
python run_anndata.py
```

The indices follow the `obs_names` order:

| Index | AnnData observation |
| ---: | --- |
| `0` | `reference_1` |
| `1` | `reference_2` |
| `2` | `treatment_1` |
| `3` | `treatment_2` |

## Sparse AnnData matrices

When `adata.X` is sparse, PyGAGE converts it to a dense array at the input
boundary. Check available memory before converting a very large object. A
smaller gene-by-sample table containing the required genes and samples can be a
practical analysis input.

## AnnData checklist

Confirm:

- observations are samples;
- variables are genes;
- `var_names` use the gene-set identifier system;
- `obs_names` clearly identify sample order;
- reference and sample indices follow that order;
- `.X` contains the intended matrix or transformed layer copied into `.X`; and
- the returned Polars results are saved with the analysis settings.

[<- Previous: Use pre-ranked data](13-preranked.md) | [Home](index.md) | [Next: Download KEGG gene sets ->](15-kegg.md)
