# Use advanced analysis options

*Page 21 of 31*

Use this page after the standard workflow is working and your analysis plan
calls for extra output or a specialized background. These options belong to
the Python API:

- control-gene background;
- global directional adjustment;
- effect sizes;
- leading-edge genes;
- permutation p-values;
- parallel workers; and
- a reproducible random seed.

The standard analysis remains:

```python
analysis.run_gage(prepared_data, gene_sets)
```

Add an option deliberately and save the setting with the result.

## Complete advanced example

Create `advanced_analysis.py`:

```python
from pathlib import Path

import polars as pl
from pygage import GAGEAnalysis


prepared_data = pl.DataFrame(
    {
        "gene_id": [
            "1", "2", "3", "4", "5", "6",
            "7", "8", "9", "10", "11", "12",
        ],
        "change_1": [
            2.4, 2.0, 1.8, 1.5, -0.2, 0.1,
            -1.8, -2.1, -1.5, -1.2, 0.3, -0.1,
        ],
        "change_2": [
            2.2, 1.9, 1.6, 1.4, 0.0, 0.2,
            -1.7, -1.9, -1.4, -1.1, 0.2, 0.0,
        ],
        "change_3": [
            2.1, 1.7, 1.5, 1.3, 0.1, 0.0,
            -1.6, -1.8, -1.3, -1.0, 0.1, -0.2,
        ],
    }
)

gene_sets = {
    "Growth pathway": ["1", "2", "3", "4"],
    "Stress pathway": ["7", "8", "9", "10"],
    "Mixed pathway": ["3", "5", "8", "11"],
}

control_genes = [
    "5", "6", "11", "12",
]

analysis = GAGEAnalysis()
tables = analysis.run_gage(
    prepared_data,
    gene_sets,
    set_size_range=(2, 10),
    test_method="t-test",
    meta_method="stouffer",
    same_dir=True,
    fdr_method="BH",
    control_genes=control_genes,
    global_bh=True,
    compute_effect=True,
    leading_edge=True,
    permutations=100,
    n_jobs=1,
    random_state=2026,
)

output_folder = Path("advanced_output")
output_folder.mkdir(exist_ok=True)

tables["greater"].write_csv(
    output_folder / "greater_results.csv"
)
tables["less"].write_csv(
    output_folder / "less_results.csv"
)

print(
    tables["greater"].select(
        [
            "gene_set",
            "q_val",
            "effect",
            "leading_edge",
            "p_perm",
        ]
    )
)
print("Finished! Open the advanced_output folder.")
```

Run:

```bash
python advanced_analysis.py
```

This teaching script uses a small set-size range and 100 permutations so it
finishes quickly. A real protocol may use a larger planned permutation count.

## Use a control-gene background

The standard background contains all measured genes:

```python
control_genes=None
```

Provide a list when a defined set of control genes should be the reference
background:

```python
control_genes = ["5", "6", "11", "12"]

tables = analysis.run_gage(
    prepared_data,
    gene_sets,
    control_genes=control_genes,
)
```

The IDs must use the same identifier system as `prepared_data`. Keep the
control-gene list with the analysis record.

## Choose per-direction or global BH adjustment

The standard setting is:

```python
global_bh=False
```

With separate `greater` and `less` results, Benjamini–Hochberg adjustment is
then applied within each direction.

Use:

```python
global_bh=True
```

to adjust across the union of the greater and less p-values. This changes the
family of tests being adjusted, so state the choice in the methods.

## Include the effect column

The default is:

```python
compute_effect=True
```

The resulting `effect` is the mean prepared value across the matched members
of that set. For log2 fold-change input:

- positive effect means a positive average member change;
- negative effect means a negative average member change; and
- a value near zero means the average signed change is near zero.

Keep the statistic, q-value, and effect together when interpreting a row.

## Include leading-edge genes

Request:

```python
leading_edge=True
```

The `leading_edge` column contains up to 25 strongly contributing matched
member IDs, separated by semicolons:

```text
gene_1;gene_2;gene_3
```

Split that value in Python with:

```python
genes = leading_edge_text.split(";")
```

Use these IDs to return to the expression data, inspect individual genes, or
prepare a focused table. Page 22 shows the export workflow.

## Include a permutation p-value

Request a positive number of permutations:

```python
permutations=1000
```

PyGAGE then adds `p_perm`. A larger number gives finer p-value resolution and
takes longer to calculate.

Use a recorded seed:

```python
random_state=2026
```

The same data, settings, software version, permutation count, and seed make
the random part of the workflow repeatable.

## Choose the worker count

The safest shared-computer setting is:

```python
n_jobs=1
```

Other choices are:

| Value | Meaning |
| --- | --- |
| `1` | one worker; standard default |
| `4` | up to four workers for the gene-set loop |
| `-1` | let the thread executor use the available cores |

Use the number assigned by a cluster scheduler or lab-computer policy. Page 27
shows how to coordinate PyGAGE, Polars, and numerical-library thread limits.

## Filter both directions in a defined way

`SignificanceFilter` handles a set that passes the cutoff in both directions:

```python
from pygage.results_analysis import SignificanceFilter


filtered = SignificanceFilter.filter_significant(
    tables,
    cutoff=0.05,
    use_q=True,
    dual_sig=2,
)
```

The `dual_sig` choices are:

| Value | Rule |
| --- | --- |
| `0` | omit a set that passes in both directions |
| `1` | keep only its better-scoring direction |
| `2` | retain both directional rows |

The default is `2`. Pick the rule before comparing conditions and record it.

For the result most recently produced by one `GAGEAnalysis` object, the simpler
filter is:

```python
filtered = analysis.filter_significant(
    cutoff=0.05,
    use_q=True,
)
```

The typed result object supports the same simple filter:

```python
filtered = analysis.result_obj.significant(
    cutoff=0.05,
    use_q=True,
)
```

## Save an advanced analysis record

Record all options that differ from the defaults:

```text
control-gene file: control_genes.txt
BH family: greater and less combined
effect: included
leading edge: included
permutations: 1000
workers: 4
random seed: 2026
```

Also keep the unfiltered output. A future reader can then reproduce the
filtering without rerunning the enrichment.

[<- Previous: Choose statistical settings](20-statistical-settings.md) | [Home](index.md) | [Next: Filter, group, compare, and export ->](22-group-overlap.md)
