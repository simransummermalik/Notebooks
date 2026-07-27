# Read and prepare an expression matrix

*Page 8 of 31*

Preparation converts sample measurements into one or more gene-level
comparison columns. This page runs the preparation separately so you can
inspect exactly what PyGAGE will analyze.

## Complete preparation script

Create `prepare_expression.py`:

```python
from pygage import GAGEPreparation, read_matrix


# Read genes x samples from the CSV file.
expression = read_matrix(
    "expression.csv",
    gene_col="gene_id",
)

# Calculate treatment-minus-reference values.
prepared = GAGEPreparation.prepare_expression(
    expression_data=expression,
    ref_indices=[0, 1],
    samp_indices=[2, 3],
    gene_col="gene_id",
    comparison="paired",
    same_dir=True,
    use_fold=True,
    input_logged=True,
    rank_test=False,
)

# Save and display the prepared table.
prepared.write_csv("prepared_expression.csv")

print(prepared)
print("Saved prepared_expression.csv")
```

Run:

```bash
python prepare_expression.py
```

The new file begins like this:

```text
gene_id,treatment_1,treatment_2
1,2.4,2.2
2,2.0,1.9
3,1.8,1.6
```

Small floating-point displays such as `2.4000000000000004` have the same
numeric meaning.

## Exact preparation signature

PyGAGE 1.2.1 provides:

```python
GAGEPreparation.prepare_expression(
    expression_data,
    ref_indices=None,
    samp_indices=None,
    gene_col="gene_id",
    comparison="paired",
    same_dir=True,
    use_fold=True,
    input_logged=True,
    rank_test=False,
)
```

It returns a Polars DataFrame.

## Explain every argument

| Argument | Default | Meaning |
| --- | --- | --- |
| `expression_data` | required | genes-by-samples Polars table |
| `ref_indices` | `None` | zero-based reference positions; `None` means values are already prepared |
| `samp_indices` | `None` | zero-based comparison positions; with references supplied, `None` selects all non-reference columns |
| `gene_col` | `"gene_id"` | identifier-column name |
| `comparison` | `"paired"` | paired, unpaired, group-mean, or one-versus-group preparation |
| `same_dir` | `True` | preserve positive and negative directions |
| `use_fold` | `True` | calculate fold-change-style differences |
| `input_logged` | `True` | input is already logged |
| `rank_test` | `False` | preserve values instead of replacing each column with ranks |

For raw non-log values, change only:

```python
input_logged=False
```

PyGAGE then applies `log2(x + 1)` before calculating differences.

## Output shape by comparison

Suppose the input has `G` genes, `R` reference columns, and `S` sample columns.

| Comparison | Prepared numeric columns |
| --- | ---: |
| `paired` | `S` |
| `unpaired` | `S × R` |
| `as.group` | `1` |
| `1ongroup` | `S` |

The gene-ID column is also retained.

Column naming:

- paired and one-versus-group output uses sample names;
- unpaired output uses `sample_vs_reference`; and
- group-mean output is named `mean.fc`.

## Already prepared data

When a table already contains gene-level changes or statistics, no references
are needed:

```python
prepared = GAGEPreparation.prepare_expression(
    expression_data=already_prepared,
    ref_indices=None,
    gene_col="gene_id",
)
```

The gene column and numeric value columns pass through as the prepared matrix.
The one-call route can express the same intent with `prepared=True`.

## Rank transformation

`rank_test=True` ranks every prepared column across genes. It is an advanced
preparation choice. The analysis engine also performs the rank handling needed
for `test_method="ks-test"`, described on page 20.

## Preparation checklist

Open `prepared_expression.csv` and confirm:

- the gene IDs are still present;
- no original reference columns remain;
- every numeric column has a known comparison;
- paired changes use the intended sample/reference order;
- positive and negative signs have the intended biological meaning; and
- the row count matches the expected number of measured genes.

[<- Previous: Choose reference and sample columns](07-reference-and-sample.md) | [Home](index.md) | [Next: Understand gene sets ->](09-gene-sets.md)
