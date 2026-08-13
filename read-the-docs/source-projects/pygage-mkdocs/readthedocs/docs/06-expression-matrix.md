# Understand an expression matrix

*Page 6 of 31*

Use this route when every row is a gene and every measurement column is a
sample. This page creates the practice expression file used on pages 7–11.

All examples in this guide use PyGAGE 1.2.1.

## What the table must look like

```text
gene_id | reference_1 | reference_2 | treatment_1 | treatment_2
```

The two dimensions mean:

- **rows** are genes;
- **columns** are samples; and
- the special `gene_id` column names each gene.

PyGAGE expects the sample columns to contain numbers.

## 1. Create `expression.csv`

Inside `my-pygage-project`, create a plain-text file named `expression.csv`.
Paste this complete table:

```csv
gene_id,reference_1,reference_2,treatment_1,treatment_2
1,6.0,6.2,8.4,8.4
2,7.0,6.8,9.0,8.7
3,5.5,5.7,7.3,7.3
4,6.5,6.3,8.0,7.7
5,4.5,4.7,4.3,4.7
6,5.0,5.1,5.1,5.3
7,7.0,6.8,5.2,5.1
8,6.5,6.6,4.4,4.7
9,5.5,5.4,4.0,4.0
10,6.0,6.1,4.8,5.0
11,4.8,4.9,5.1,5.1
12,5.2,5.3,5.1,5.3
```

A CSV file separates columns with commas. The first line is the **header**,
which gives every column its name.

## 2. Inspect the table with PyGAGE

Create `inspect_expression.py`:

```python
from pygage import read_matrix


expression = read_matrix("expression.csv")

print("Rows:", expression.height)
print("Columns:", expression.width)
print("Column names:", expression.columns)
print(expression.head(3))
```

Run it:

```bash
python inspect_expression.py
```

The summary should report:

```text
Rows: 12
Columns: 5
Column names: ['gene_id', 'reference_1', 'reference_2', 'treatment_1', 'treatment_2']
```

`read_matrix()` returns a Polars DataFrame. A **DataFrame** is a table that
Python can inspect, transform, and save.

## Understand `read_matrix()`

The exact PyGAGE 1.2.1 signature is:

```python
read_matrix(
    source,
    gene_col="gene_id",
)
```

| Argument | Meaning |
| --- | --- |
| `source` | CSV/TSV filename or an existing table |
| `gene_col` | name to use for the gene-ID column |

If `gene_col` is not already a column name, `read_matrix()` renames the first
column. It stores that column as text so identifiers such as `100`, `TP53`, or
`K00844` remain identifiers rather than measurements.

## What the practice numbers mean

For this teaching file:

- `reference_1` is paired with `treatment_1`;
- `reference_2` is paired with `treatment_2`; and
- the values are already on a log2 expression scale.

For gene `1`, the two changes will be:

```text
treatment_1 - reference_1 = 8.4 - 6.0 = 2.4
treatment_2 - reference_2 = 8.4 - 6.2 = 2.2
```

PyGAGE performs these subtractions during preparation.

## Raw values versus logged values

Write down which type you have:

| My sample columns contain | Setting used later |
| --- | --- |
| log2 expression values | `input_logged=True` |
| raw nonnegative counts or intensities | `input_logged=False` |

With `input_logged=False`, PyGAGE first applies:

```text
log2(value + 1)
```

Do not choose the setting from the size of the numbers alone. Check the method
that produced the file.

## Input checklist

Before continuing, confirm:

- one row represents one gene;
- one column represents one sample;
- the gene column has a clear name;
- sample columns contain numeric measurements;
- sample names are unique;
- gene identifiers use one documented system;
- reference and comparison samples are known; and
- you know whether the measurements are already logged.

[<- Previous: Choose your input route](05-choose-input.md) | [Home](index.md) | [Next: Choose reference and sample columns ->](07-reference-and-sample.md)
