# Use pre-ranked data

*Page 13 of 31*

A pre-ranked input assigns one numeric score to every gene. Higher and lower
scores define the two ends of the ranking.

This page uses the PyGAGE 1.2.1 pre-ranked input adapter.

## Accepted shape

```text
gene_id | score
```

The score could be a signed statistic, correlation, log2 fold change, or
another documented gene-level ranking value.

## Complete dictionary workflow

Create `run_preranked.py`:

```python
import json
from pathlib import Path

import polars as pl
from pygage import gage, read_preranked


scores = {
    "1": 5.2,
    "2": 4.7,
    "3": 4.2,
    "4": 3.7,
    "5": -0.4,
    "6": 0.2,
    "7": -4.1,
    "8": -4.8,
    "9": -3.5,
    "10": -3.0,
    "11": 0.6,
    "12": -0.2,
}

gene_sets = json.loads(
    Path("gene_sets.json").read_text()
)

ranked = read_preranked(scores)

results = gage(
    data=ranked,
    gene_sets=gene_sets,
    prepared=True,
    set_size_range=(2, 10),
)

top_greater = (
    results
    .filter(pl.col("direction") == "greater")
    .sort("p_val")
    .head(5)
)
top_less = (
    results
    .filter(pl.col("direction") == "less")
    .sort("p_val")
    .head(5)
)

ranked.write_csv("ranked_input.csv")
results.write_csv("preranked_results.csv")

print("Top greater sets:")
print(top_greater)
print("Top less sets:")
print(top_less)
```

Run:

```bash
python run_preranked.py
```

The dictionary keys become `gene_id`; the dictionary values become `score`.

## Exact `read_preranked()` signature

```python
read_preranked(
    source,
    gene_col="gene_id",
    score_col="score",
)
```

It returns a two-column Polars DataFrame.

| Argument | Default | Meaning |
| --- | --- | --- |
| `source` | required | file path, `{gene: score}` dictionary, or table |
| `gene_col` | `"gene_id"` | input gene-column name |
| `score_col` | `"score"` | input score-column name |

Gene IDs are stored as text. Scores are stored as floating-point numbers.

## Read a pre-ranked file

For a file named `my_ranking.csv`:

```csv
gene_id,score
1,5.2
2,4.7
3,4.2
```

use:

```python
ranked = read_preranked(
    "my_ranking.csv",
    gene_col="gene_id",
    score_col="score",
)
```

If the requested names are absent, the reader uses the first column as genes
and the second as scores. Clear headers are safer for a reproducible project.

## Direction of the score

Before analysis, write one sentence such as:

```text
Positive scores mean higher expression in treatment.
Negative scores mean lower expression in treatment.
```

PyGAGE's `greater` and `less` directions inherit that meaning. Reversing every
score reverses the interpretation of the two ends.

## Default versus rank-based testing

The example uses the default:

```python
test_method="t-test"
```

For a rank-based two-sample test, use:

```python
results = gage(
    ranked,
    gene_sets,
    prepared=True,
    set_size_range=(2, 10),
    test_method="ks-test",
)
```

Page 20 compares the t-test, z-test, and KS choices.

## Pre-ranked checklist

Confirm:

- one row or dictionary item represents one gene;
- every score is numeric;
- the sign and magnitude have documented meanings;
- IDs match the gene-set collection;
- duplicate-gene handling occurred before ranking; and
- `prepared=True` is used for clarity.

[<- Previous: Use a differential-expression table](12-de-tables.md) | [Home](index.md) | [Next: Use pandas or AnnData ->](14-pandas-anndata.md)
