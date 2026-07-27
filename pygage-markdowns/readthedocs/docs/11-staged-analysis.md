# Run the staged PyGAGE workflow

*Page 11 of 31*

The staged workflow performs preparation and analysis as two visible steps.
Use it when you want to inspect the prepared matrix, access each directional
table separately, or configure the full analysis engine.

The signatures and defaults on this page are from PyGAGE 1.2.1.

## Workflow

```text
expression matrix
        |
        v
GAGEPreparation.prepare_expression()
        |
        v
prepared gene-level changes
        |
        v
GAGEAnalysis.run_gage()
        |
        v
greater + less + stats
```

## Complete staged script

Create `run_staged.py`:

```python
import json
from pathlib import Path

from pygage import (
    GAGEAnalysis,
    GAGEPreparation,
    read_matrix,
)


expression = read_matrix("expression.csv")
gene_sets = json.loads(
    Path("gene_sets.json").read_text()
)

prepared = GAGEPreparation.prepare_expression(
    expression_data=expression,
    ref_indices=[0, 1],
    samp_indices=[2, 3],
    gene_col="gene_id",
    comparison="paired",
    same_dir=True,
    input_logged=True,
)

analysis = GAGEAnalysis()

results = analysis.run_gage(
    expression_data=prepared,
    gene_sets=gene_sets,
    gene_col="gene_id",
    set_size_range=(2, 10),
    same_dir=True,
    test_method="t-test",
    meta_method="stouffer",
    fdr_method="BH",
    control_genes=None,
    global_bh=False,
    compute_effect=True,
    leading_edge=False,
    permutations=0,
    n_jobs=1,
    random_state=0,
)

significant = analysis.filter_significant(
    cutoff=0.05,
    use_q=True,
)

output_folder = Path("staged_results")
output_folder.mkdir(exist_ok=True)

prepared.write_csv(
    output_folder / "prepared_expression.csv"
)
results["greater"].write_csv(
    output_folder / "greater.csv"
)
results["less"].write_csv(
    output_folder / "less.csv"
)
results["stats"].write_csv(
    output_folder / "stats.csv"
)
significant["greater"].write_csv(
    output_folder / "significant_greater.csv"
)
significant["less"].write_csv(
    output_folder / "significant_less.csv"
)

print("Top greater result:")
print(results["greater"].head(1))
print("Top less result:")
print(results["less"].head(1))
print("Saved files in staged_results")
```

Run:

```bash
python run_staged.py
```

## Exact analysis signature

```python
GAGEAnalysis.run_gage(
    expression_data,
    gene_sets,
    gene_col="gene_id",
    set_size_range=(10, 500),
    same_dir=True,
    test_method="t-test",
    meta_method="stouffer",
    fdr_method="BH",
    control_genes=None,
    global_bh=False,
    compute_effect=True,
    leading_edge=False,
    permutations=0,
    n_jobs=1,
    random_state=0,
)
```

It returns a dictionary of Polars DataFrames.

## Explain every analysis argument

| Argument | Default | Job |
| --- | --- | --- |
| `expression_data` | required | prepared gene-ID plus value columns |
| `gene_sets` | required | groups to test |
| `gene_col` | `"gene_id"` | identifier-column name |
| `set_size_range` | `(10, 500)` | inclusive present-member limits |
| `same_dir` | `True` | produce greater and less tables |
| `test_method` | `"t-test"` | t, z, or KS set test |
| `meta_method` | `"stouffer"` | Stouffer or Fisher combination |
| `fdr_method` | `"BH"` | Benjamini–Hochberg q-values |
| `control_genes` | `None` | use all measured genes as background |
| `global_bh` | `False` | adjust each direction separately |
| `compute_effect` | `True` | add the `effect` column |
| `leading_edge` | `False` | optionally add driving members |
| `permutations` | `0` | optionally calculate `p_perm` |
| `n_jobs` | `1` | worker count for gene sets |
| `random_state` | `0` | permutation random seed |

Page 20 explains test, meta, direction, and FDR choices. Page 21 explains
control genes, global BH, effects, leading-edge genes, and permutations.

## Understand the result dictionary

```python
results["greater"]
```

Positive-direction ranking, sorted from smallest `p_val`.

```python
results["less"]
```

Negative-direction ranking, present when `same_dir=True`.

```python
results["stats"]
```

A compact table containing only:

```text
gene_set | stat_mean | set_size
```

With `same_dir=False`, the dictionary has `greater` and `stats` but no `less`.

## Stored analysis state

After `run_gage()`:

```python
analysis.results
```

contains the same dictionary.

```python
analysis.result_obj
```

is a typed `GAGEResult` with:

- `.greater`
- `.less`
- `.stats`
- `.meta`
- `.as_dict()`
- `.significant(cutoff=0.1, use_q=True)`

The metadata records the test method, meta method, number of prepared columns,
and directional setting.

## Engine filter

```python
analysis.filter_significant(
    cutoff=0.1,
    use_q=True,
)
```

uses `q_val` by default. Set `use_q=False` to filter `p_val`. The comparison is
strictly less than the cutoff. The compact `stats` table is returned unchanged.

[<- Previous: Run the one-call workflow](10-one-call-gage.md) | [Home](index.md) | [Next: Use a differential-expression table ->](12-de-tables.md)
