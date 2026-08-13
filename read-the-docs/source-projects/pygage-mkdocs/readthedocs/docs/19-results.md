# Understand every result column

*Page 19 of 31*

Use this page after an analysis has produced a PyGAGE result table. It explains
how to sort, filter, save, and report the result without changing the
statistical test.

## Start with the two result formats

The high-level `gage()` function returns one tidy Polars DataFrame by default:

```text
all greater rows
        +
all less rows
        |
        v
one table with a direction column
```

The staged `GAGEAnalysis.run_gage()` workflow returns a dictionary:

```python
{
    "greater": greater_table,
    "less": less_table,
    "stats": statistics_table,
}
```

Both formats contain the same core enrichment information. The tidy format is
convenient for saving, filtering, and plotting. The dictionary keeps the two
directions in separate tables.

## Every standard tidy-result column

| Column | Meaning |
| --- | --- |
| `gene_set` | gene-set or pathway name |
| `set_size` | number of set members found in the input data |
| `stat_mean` | mean gene-set statistic across prepared comparison columns |
| `p_geomean` | geometric mean of the directional per-column p-values |
| `p_val` | p-value combined across prepared columns |
| `q_val` | multiple-testing-adjusted p-value |
| `effect` | mean change across matched genes when effect calculation is enabled |
| `direction` | `greater` or `less` |

Optional advanced columns are:

| Column | When it appears | Meaning |
| --- | --- | --- |
| `leading_edge` | `leading_edge=True` | up to 25 member genes contributing strongly to the signal |
| `p_perm` | `permutations` is greater than zero | sample-label permutation p-value |

## Interpret `direction` together with the input

`greater` and `less` describe the direction of the supplied numbers:

| Input value | `greater` means | `less` means |
| --- | --- | --- |
| log2 fold change | members tend toward positive change | members tend toward negative change |
| differential-expression statistic | members tend toward positive statistic | members tend toward negative statistic |
| prepared sample-minus-reference change | members tend higher in the sample | members tend lower in the sample |
| another documented score | members tend toward larger scores | members tend toward smaller scores |

Always state what the numerical input means before interpreting direction.

## Understand `set_size`

`set_size` counts the members that matched the measured-gene universe.

Example:

```text
source gene set: 180 members
members present in the input: 142
reported set_size: 142
```

The source collection size and matched size can differ because not every
source member is present in every dataset.

## Understand `stat_mean`

PyGAGE calculates a gene-set statistic for every prepared comparison column.
`stat_mean` is their mean:

- a positive value supports the `greater` direction;
- a negative value supports the `less` direction; and
- a larger absolute value represents a stronger average separation from the
  background.

Use the p-value and q-value to evaluate statistical evidence.

## Understand p-values and q-values

`p_val` combines evidence across the prepared columns with the chosen
meta-method.

`q_val` adjusts for testing many gene sets. The standard configuration uses
Benjamini–Hochberg adjustment separately in each direction.

A result-filtering rule may be:

```text
q_val < 0.05
```

Choose the rule as part of the analysis plan and report it with the result.

## Understand `effect`

With the standard setting:

```python
compute_effect=True
```

PyGAGE adds `effect`, the mean prepared change across matched members of the
gene set.

The statistic, effect, and q-value answer different questions:

| Value | Main question |
| --- | --- |
| `stat_mean` | how strongly does the set differ from the background? |
| `effect` | what is the average prepared member change? |
| `q_val` | how strong is the evidence after multiple-testing adjustment? |

Use them together rather than treating one column as the entire interpretation.

## Review the page 3 result file

Create `review_results.py` beside the `pygage_output` folder:

```python
from pathlib import Path

import polars as pl


results = pl.read_csv(
    Path("pygage_output") / "all_results.csv"
)

greater = (
    results
    .filter(pl.col("direction") == "greater")
    .sort("q_val")
)

less = (
    results
    .filter(pl.col("direction") == "less")
    .sort("q_val")
)

significant = (
    results
    .filter(pl.col("q_val") < 0.05)
    .sort(["direction", "q_val"])
)

print("Top greater rows:")
print(greater.head(5))

print("Top less rows:")
print(less.head(5))

print("Rows with q_val below 0.05:")
print(significant)

significant.write_csv(
    Path("pygage_output") / "reviewed_results.csv"
)
```

Run:

```bash
python review_results.py
```

This script reads an existing result. It does not rerun the enrichment.

## Capture dictionary results

Ask the high-level function for the staged dictionary with:

```python
result_tables = gage(
    data,
    gene_sets,
    prepared=True,
    tidy=False,
)

greater = result_tables["greater"]
less = result_tables["less"]
stats = result_tables["stats"]
```

The `stats` table contains:

```text
gene_set | stat_mean | set_size
```

Use this format when later code expects separate direction tables.

## Use the typed result object

After the staged workflow:

```python
analysis = GAGEAnalysis()
tables = analysis.run_gage(prepared, gene_sets)
typed_result = analysis.result_obj
```

`typed_result` is a `GAGEResult` with:

```python
typed_result.greater
typed_result.less
typed_result.stats
typed_result.meta
```

The metadata records:

- test method;
- meta-method;
- number of prepared comparison columns; and
- whether directions were analyzed separately.

Filter through the typed object:

```python
filtered = typed_result.significant(
    cutoff=0.05,
    use_q=True,
)
```

## Save the analysis record

Keep these items together:

- complete unfiltered result;
- filtered result and cutoff;
- input table;
- gene-set file and its source/release;
- identifier system;
- preparation settings;
- test and meta-method;
- set-size range;
- PyGAGE and Python versions; and
- script or notebook.

## Reporting sentence template

Adapt this sentence:

> Gene-set enrichment was performed with PyGAGE 1.2.1 using [test method],
> [meta-method], a matched set-size range of [minimum–maximum], and
> Benjamini–Hochberg adjustment. Sets with [q-value rule] were retained.
> Positive and negative directions represent [meaning in this analysis].

[<- Previous: Use Reactome, MSigDB, GMT, and the cache](18-other-gene-sets.md) | [Home](index.md) | [Next: Choose statistical settings ->](20-statistical-settings.md)
