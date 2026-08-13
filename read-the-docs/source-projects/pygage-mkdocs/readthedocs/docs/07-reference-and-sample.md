# Choose reference and sample columns

*Page 7 of 31*

PyGAGE needs to know which samples provide the reference and which samples are
being compared with that reference.

The positions and comparison modes below are those used by PyGAGE 1.2.1.

## The sample-column numbering rule

PyGAGE uses zero-based positions among the measurement columns. It does **not**
count `gene_id`.

For `expression.csv`:

| PyGAGE index | Column | Role |
| ---: | --- | --- |
| `0` | `reference_1` | reference |
| `1` | `reference_2` | reference |
| `2` | `treatment_1` | sample |
| `3` | `treatment_2` | sample |

The practice lists are therefore:

```python
ref_indices = [0, 1]
samp_indices = [2, 3]
```

Square brackets make a Python list. The commas separate its items.

## Check the numbering instead of guessing

Create `show_sample_plan.py`:

```python
from pygage import read_matrix


expression = read_matrix("expression.csv")
gene_column = "gene_id"

sample_columns = [
    name
    for name in expression.columns
    if name != gene_column
]

print("PyGAGE sample-column positions:")
for index, name in enumerate(sample_columns):
    print(index, "->", name)

ref_indices = [0, 1]
samp_indices = [2, 3]

print(
    "References:",
    [sample_columns[index] for index in ref_indices],
)
print(
    "Samples:",
    [sample_columns[index] for index in samp_indices],
)
```

Run:

```bash
python show_sample_plan.py
```

The final two lines identify the two reference columns and two treatment
columns.

## Choose the comparison design

`comparison` controls how the selected columns are contrasted.

### Paired

```python
comparison="paired"
```

Use paired analysis when each sample has one matched reference:

```text
reference_1 <-> treatment_1
reference_2 <-> treatment_2
```

PyGAGE subtracts each reference from its matching sample. Keep the lists in
matching order and use equal list lengths for a straightforward paired design.

### Unpaired

```python
comparison="unpaired"
```

Use unpaired analysis for two groups without one-to-one matching. Every sample
is compared with every reference:

```text
treatment_1 - reference_1
treatment_1 - reference_2
treatment_2 - reference_1
treatment_2 - reference_2
```

Two samples and two references therefore create four prepared columns.

### Compare group means

```python
comparison="as.group"
```

PyGAGE creates one column:

```text
mean(all selected samples) - mean(all selected references)
```

Choose this when the group-average contrast is the planned gene-level
measurement.

### Compare each sample with the reference mean

```python
comparison="1ongroup"
```

PyGAGE subtracts the mean of the references from each sample:

```text
treatment_1 - reference mean
treatment_2 - reference mean
```

The alias `"as.ref"` performs the same preparation.

## Let PyGAGE choose all non-reference samples

If every column outside `ref_indices` is a comparison sample, this is valid:

```python
samp_indices=None
```

For beginner projects, writing both lists explicitly makes the analysis plan
easier to check and reproduce.

## Directional or magnitude-only changes

The standard setting is:

```python
same_dir=True
```

It preserves positive and negative changes so PyGAGE can report separate
`greater` and `less` directions.

With:

```python
same_dir=False
```

preparation uses absolute changes. Positive and negative movement both count as
change magnitude. Use the same `same_dir` value in preparation and analysis.

## Record the decision

For the practice workflow, save this plan in your notes:

```text
gene column: gene_id
references: reference_1, reference_2
samples: treatment_1, treatment_2
reference indices: 0, 1
sample indices: 2, 3
comparison: paired
input already logged: yes
same direction: yes
```

[<- Previous: Understand an expression matrix](06-expression-matrix.md) | [Home](index.md) | [Next: Read and prepare the matrix ->](08-prepare-expression.md)
