# Understand the first enrichment

*Page 4 of 31*

This page explains what PyGAGE did in the practice analysis without adding new
code.

## The analysis had two layers

PyGAGE first examined each measurement column and then combined the evidence
across the two columns:

```text
test each gene set in sample_change_1
                    +
test each gene set in sample_change_2
                    |
                    v
one combined result per gene set and direction
```

This two-level design is the central GAGE workflow.

## The measured genes formed the background

The practice table contained twelve genes. For each measurement column,
PyGAGE compared the member values of a gene set with the measured-gene
background.

For `Growth pathway`, the member genes were:

```text
1, 2, 3, 4
```

Their values were consistently positive in both prepared columns. The set
therefore received strong evidence in the `greater` direction.

For `Stress pathway`, the member genes were:

```text
7, 8, 9, 10
```

Their values were consistently negative. The set received strong evidence in
the `less` direction.

## Greater and less are separate questions

With the standard directional analysis, PyGAGE asks:

1. does this gene set tend toward higher values?
2. does this gene set tend toward lower values?

The result therefore contains a `greater` row and a `less` row for each tested
set.

| Direction | Teaching interpretation |
| --- | --- |
| `greater` | set members tend toward higher or more positive values |
| `less` | set members tend toward lower or more negative values |

For real data, replace “higher” and “lower” with the meaning of the supplied
measurement.

## One result row contains several summaries

| Column | First meaning |
| --- | --- |
| `gene_set` | name of the tested group |
| `set_size` | number of member genes found in the measurement table |
| `stat_mean` | average direction and strength of the per-column statistic |
| `p_geomean` | geometric mean of the per-column p-values |
| `p_val` | p-value combined across measurement columns |
| `q_val` | p-value adjusted for testing many gene sets |
| `effect` | average member change when effect calculation is enabled |
| `direction` | `greater` or `less` |

Page 19 gives the complete interpretation and reporting guidance for every
column.

## Why use a q-value?

An enrichment analysis may test hundreds or thousands of gene sets. Testing
many sets increases the chance of seeing a small p-value by chance.

The q-value applies a multiple-testing adjustment. PyGAGE uses
Benjamini–Hochberg adjustment by default.

In the practice script:

```text
q_val < 0.05
```

was the teaching significance rule.

## Set size means matched members

The teaching sets each listed four genes, and all four were present in the
measurement table:

```text
set_size = 4
```

In a real analysis, a gene set may list 200 genes while only 150 appear in the
input. Its reported `set_size` is then 150.

This is why matching identifier systems is essential.

## The teaching data establish workflow, not biology

The set names and values on page 3 were created to make the two directions
easy to see. A real interpretation needs:

- experimentally measured or calculated values;
- a documented comparison;
- a biologically appropriate gene-set collection;
- a planned statistical configuration; and
- subject-matter review.

## The next decision

Choose the row that describes your own starting data on page 5. That page
connects each starting format to a complete tutorial.

[<- Previous: Run your first enrichment](03-first-enrichment.md) | [Home](index.md) | [Next: Choose your input route ->](05-choose-input.md)
