# Choose statistical settings

*Page 20 of 31*

Use this page when you are deciding which statistical options belong in your
analysis. The standard PyGAGE settings are a strong starting point:

```python
test_method="t-test"
meta_method="stouffer"
same_dir=True
set_size_range=(10, 500)
fdr_method="BH"
```

These defaults follow the main GAGE workflow. Change one only when the change
answers a scientific or design question in your study.

## The beginner decision table

| Question | Beginner choice | Why |
| --- | --- | --- |
| Which gene-set test? | `test_method="t-test"` | standard GAGE set-versus-background test |
| How should evidence across columns be combined? | `meta_method="stouffer"` | standard GAGE cross-column combination |
| Do positive and negative changes matter separately? | `same_dir=True` | creates separate `greater` and `less` results |
| Which matched set sizes should be tested? | `set_size_range=(10, 500)` | avoids very small and extremely broad sets |
| How should many tests be adjusted? | `fdr_method="BH"` | creates Benjamini–Hochberg q-values |
| Which value should usually be filtered? | `q_val` | accounts for testing many gene sets |

## Understand the two levels of a PyGAGE test

PyGAGE performs two connected steps:

1. For each prepared data column, it compares the members of a gene set with
   the measured-gene background.
2. When there is more than one prepared column, it combines the evidence into
   one result for that gene set.

The first step is controlled by `test_method`. The second is controlled by
`meta_method`.

```text
prepared gene values
        |
        v
test each gene set in each column       <- test_method
        |
        v
combine evidence across columns         <- meta_method
        |
        v
p-value, q-value, statistic, direction
```

## Choose a test method

PyGAGE provides three test methods.

| Setting | Plain-language description | A sensible use |
| --- | --- | --- |
| `"t-test"` | compares the set mean with the whole-array background while accounting for variation | standard first analysis |
| `"z-test"` | compares the set mean with the background using a PAGE-style z statistic | a planned z-test workflow or comparison with an earlier PAGE-style analysis |
| `"ks-test"` | compares ranks rather than only the mean | a planned rank-based analysis |

Set the method inside `gage()`:

```python
result = gage(
    prepared_data,
    gene_sets,
    prepared=True,
    test_method="t-test",
)
```

Use the exact accepted spelling:

```text
t-test
z-test
ks-test
```

## Choose a meta-method

When the prepared table has several measurement columns, each column provides
evidence. PyGAGE offers two ways to combine it.

| Setting | Meaning |
| --- | --- |
| `"stouffer"` | converts column p-values to z scores and combines them |
| `"fisher"` | combines the negative logarithms of the column p-values |

The standard choice is:

```python
meta_method="stouffer"
```

Use Fisher combination only when it belongs in the analysis plan:

```python
meta_method="fisher"
```

The meta-method does not replace biological replication. It combines the
per-column evidence produced from the prepared input.

## Choose directional or magnitude-only analysis

With:

```python
same_dir=True
```

PyGAGE reports:

- `greater`, for sets whose members tend toward larger values; and
- `less`, for sets whose members tend toward smaller values.

With:

```python
same_dir=False
```

PyGAGE uses the magnitude of change and returns a directionless ranking. This
is appropriate when the size of a change matters but its sign is not the
scientific question.

For log2 fold-change input, keep `same_dir=True` when up- and down-regulation
should be interpreted separately.

## Choose the matched set-size range

The range:

```python
set_size_range=(10, 500)
```

means:

- test a set when at least 10 of its members occur in the input; and
- test it when no more than 500 of its members occur in the input.

This uses the **matched** size, not necessarily the complete size in the source
database.

Write a different range only when it is justified for the collection and
study. Record the range in the methods and keep the same range when comparing
conditions.

## Use Benjamini–Hochberg adjustment

An analysis tests many gene sets, so PyGAGE adjusts the p-values:

```python
fdr_method="BH"
```

The resulting `q_val` column is the Benjamini–Hochberg-adjusted p-value. With
the standard directional analysis, adjustment is performed within each
direction.

Choose and record a filtering rule, for example:

```python
significant = result.filter(
    pl.col("q_val") < 0.05
)
```

The cutoff is a study decision. `0.05` is a common teaching example, while a
protocol may specify another value.

## Run the three test methods side by side

Create `compare_methods.py` beside the Page 3 script:

```python
from pathlib import Path

import polars as pl
from pygage import gage


prepared_data = pl.DataFrame(
    {
        "gene_id": [
            "1", "2", "3", "4", "5", "6",
            "7", "8", "9", "10", "11", "12",
        ],
        "sample_change_1": [
            2.4, 2.0, 1.8, 1.5, -0.2, 0.1,
            -1.8, -2.1, -1.5, -1.2, 0.3, -0.1,
        ],
        "sample_change_2": [
            2.2, 1.9, 1.6, 1.4, 0.0, 0.2,
            -1.7, -1.9, -1.4, -1.1, 0.2, 0.0,
        ],
    }
)

gene_sets = {
    "Growth pathway": ["1", "2", "3", "4"],
    "Stress pathway": ["7", "8", "9", "10"],
    "Mixed pathway": ["3", "5", "8", "11"],
}

output_folder = Path("method_comparison")
output_folder.mkdir(exist_ok=True)

methods = ["t-test", "z-test", "ks-test"]

for method in methods:
    result = gage(
        prepared_data,
        gene_sets,
        prepared=True,
        set_size_range=(2, 10),
        test_method=method,
        meta_method="stouffer",
        same_dir=True,
    )

    file_name = method.replace("-", "_") + "_results.csv"
    result.write_csv(output_folder / file_name)

    print(f"\nTop rows for {method}:")
    print(
        result
        .sort("q_val")
        .select(
            [
                "gene_set",
                "direction",
                "stat_mean",
                "q_val",
            ]
        )
        .head(4)
    )

print("\nFinished! Open the method_comparison folder.")
```

Run:

```bash
python compare_methods.py
```

The folder will contain:

```text
method_comparison/
├── ks_test_results.csv
├── t_test_results.csv
└── z_test_results.csv
```

The script keeps the data, gene sets, meta-method, directions, and size range
fixed. Only the test method changes. That makes the comparison interpretable.

## Record the settings

Save a small text file or notebook cell with:

```text
test_method: t-test
meta_method: stouffer
same_dir: true
set_size_range: 10 to 500 matched genes
fdr_method: BH
result rule: q_val below 0.05
```

Also record the input value type, comparison design, identifier system,
gene-set source and release, and PyGAGE version.

## Advanced formulas

You can run PyGAGE without using the formulas directly. For readers documenting
the method precisely, the standard t-test route works as follows.

For gene set \(S\) with \(n\) matched members in prepared column \(j\),
PyGAGE compares the set mean with the whole-array background mean. It creates a
per-column test statistic and directional p-values. Across \(n_c\) prepared
columns, Stouffer combination is:

\[
p_{\mathrm{combined}} =
\Phi\left(
\frac{\sum_j \Phi^{-1}(p_j)}{\sqrt{n_c}}
\right)
\]

PyGAGE also reports:

\[
p_{\mathrm{geomean}} =
\exp\left(
\frac{\sum_j \log(p_j)}{n_c}
\right)
\]

The complete analysis then applies the chosen multiple-testing adjustment to
the combined p-values.

[<- Previous: Understand every result column](19-results.md) | [Home](index.md) | [Next: Use advanced analysis options ->](21-advanced-options.md)
