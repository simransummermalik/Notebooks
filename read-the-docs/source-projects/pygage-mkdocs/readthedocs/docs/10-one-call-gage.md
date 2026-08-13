# Run the one-call `gage()` workflow

*Page 10 of 31*

`gage()` is the easiest complete PyGAGE workflow. It reads or accepts a table,
prepares raw samples when requested, runs enrichment, and returns one tidy
result table.

## Complete raw-matrix analysis

This script uses `expression.csv` from page 6 and `gene_sets.json` from page 9.
Create `run_one_call.py`:

```python
import json
from pathlib import Path

import polars as pl
from pygage import gage


gene_sets = json.loads(
    Path("gene_sets.json").read_text()
)

results = gage(
    data="expression.csv",
    gene_sets=gene_sets,
    ref_indices=[0, 1],
    samp_indices=[2, 3],
    gene_col="gene_id",
    comparison="paired",
    same_dir=True,
    test_method="t-test",
    meta_method="stouffer",
    set_size_range=(2, 10),
    input_logged=True,
    prepared=False,
    tidy=True,
)

greater = results.filter(
    pl.col("direction") == "greater"
)
less = results.filter(
    pl.col("direction") == "less"
)
significant = results.filter(
    pl.col("q_val") < 0.05
)

output_folder = Path("one_call_results")
output_folder.mkdir(exist_ok=True)

results.write_csv(output_folder / "all_results.csv")
greater.write_csv(output_folder / "greater.csv")
less.write_csv(output_folder / "less.csv")
significant.write_csv(
    output_folder / "significant.csv"
)

print(
    results.select(
        [
            "gene_set",
            "direction",
            "set_size",
            "stat_mean",
            "p_val",
            "q_val",
        ]
    )
)
print("Saved files in one_call_results")
```

Run:

```bash
python run_one_call.py
```

The teaching result places `Growth pathway` toward the top of `greater` and
`Stress pathway` toward the top of `less`.

## Exact `gage()` signature

PyGAGE 1.2.1 provides:

```python
gage(
    data,
    gene_sets,
    ref_indices=None,
    samp_indices=None,
    gene_col="gene_id",
    comparison="paired",
    same_dir=True,
    test_method="t-test",
    meta_method="stouffer",
    set_size_range=(10, 500),
    input_logged=True,
    prepared=False,
    tidy=True,
    **run_kwargs,
)
```

## Explain every argument

| Argument | Default | Meaning |
| --- | --- | --- |
| `data` | required | file path, Polars table, pandas table, AnnData object, or column dictionary |
| `gene_sets` | required | name-to-members mapping or `GeneSetCollection` |
| `ref_indices` | `None` | reference positions among non-ID columns |
| `samp_indices` | `None` | comparison-sample positions |
| `gene_col` | `"gene_id"` | gene identifier column |
| `comparison` | `"paired"` | preparation design |
| `same_dir` | `True` | return separate greater and less evidence |
| `test_method` | `"t-test"` | per-column gene-set test |
| `meta_method` | `"stouffer"` | method combining evidence across columns |
| `set_size_range` | `(10, 500)` | inclusive matched-member limits |
| `input_logged` | `True` | sample values are already logged |
| `prepared` | `False` | allow raw-matrix preparation |
| `tidy` | `True` | return one direction-labelled table |
| `**run_kwargs` | none | optional `run_gage()` settings from pages 20–21 |

`test_method` accepts `"t-test"`, `"z-test"`, or `"ks-test"`.
`meta_method` accepts `"stouffer"` or `"fisher"`.

## Understand the returned table

With standard options, each row contains:

| Column | Meaning |
| --- | --- |
| `gene_set` | tested set name |
| `set_size` | unique set members present in the input |
| `stat_mean` | average per-column set statistic |
| `p_geomean` | geometric mean of per-column directional p-values |
| `p_val` | p-value combined across columns |
| `q_val` | multiple-testing-adjusted p-value |
| `effect` | average member value/change |
| `direction` | `greater` or `less` |

Lower `p_val` and `q_val` indicate stronger evidence. Page 19 explains each
column in reporting language.

## Run an already prepared table

If page 8 created `prepared_expression.csv`, use:

```python
results = gage(
    data="prepared_expression.csv",
    gene_sets=gene_sets,
    prepared=True,
    set_size_range=(2, 10),
)
```

No reference or sample indices are needed because the numeric columns already
contain gene-level changes.

## Return separate result tables

Set:

```python
tidy=False
```

The return value is then:

```text
results["greater"]
results["less"]
results["stats"]
```

The staged workflow on page 11 uses this structure directly.

## One-call checklist

You are finished when:

- `one_call_results/all_results.csv` opens;
- both directions are present;
- each teaching set has `set_size = 4`;
- the selected comparison and logged status match the input; and
- the script and input files are saved together.

[<- Previous: Understand gene sets](09-gene-sets.md) | [Home](index.md) | [Next: Run the staged workflow ->](11-staged-analysis.md)
