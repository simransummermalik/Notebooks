# Prepare your data

Use this page when your starting file is an expression matrix that has not yet
been prepared for PyGAGE: genes in rows and biological samples in columns.

## 1. Check the table shape

A simple CSV file looks like this:

```text
gene_id,reference_1,reference_2,treatment_1,treatment_2
TP53,8.1,8.0,9.3,9.5
BRCA1,4.2,4.4,5.1,5.3
EGFR,6.3,6.1,5.6,5.4
```

The first column contains gene identifiers. Every other column contains numeric
measurements for one sample.

Keep identifiers as text, even when they contain only digits. Text preserves
letters, prefixes, and leading zeroes for exact matching.

## 2. Number only the sample columns

PyGAGE uses zero-based positions among the measurement columns. It excludes
whichever identifier column is named by `gene_col`; in this example, that
column is `gene_id`.

| PyGAGE position | Column | Planned role |
| ---: | --- | --- |
| `0` | `reference_1` | reference |
| `1` | `reference_2` | reference |
| `2` | `treatment_1` | sample |
| `3` | `treatment_2` | sample |

The corresponding lists are:

```python
ref_indices = [0, 1]
samp_indices = [2, 3]
```

You can print the positions before choosing them:

```python
from pygage import read_matrix


expression = read_matrix("expression.csv")
sample_columns = [
    name for name in expression.columns
    if name != "gene_id"
]

for position, name in enumerate(sample_columns):
    print(position, "->", name)
```

## 3. Choose the comparison design

The `comparison` setting determines how PyGAGE prepares the selected columns.

| Setting | What PyGAGE calculates | When it fits |
| --- | --- | --- |
| `"paired"` | Each sample minus its matching reference | Equal-length reference and sample lists, kept in matching order |
| `"unpaired"` | Every sample minus every reference | Two groups without one-to-one matching |
| `"as.group"` | Sample-group mean minus reference-group mean | One planned group-average comparison |
| `"1ongroup"` | Each sample minus the reference-group mean | Each sample compared with one reference average |

For the example table, paired preparation makes:

```text
treatment_1 - reference_1
treatment_2 - reference_2
```

## 4. Prepare the matrix

```python
from pygage import GAGEPreparation, read_matrix


expression = read_matrix("expression.csv")

prepared = GAGEPreparation.prepare_expression(
    expression,
    ref_indices=[0, 1],
    samp_indices=[2, 3],
    gene_col="gene_id",
    comparison="paired",
    input_logged=True,
    same_dir=True,
)

prepared.write_csv("prepared_expression.csv")
print(prepared)
```

The important settings are:

| Setting | Meaning |
| --- | --- |
| `input_logged=True` | The expression values are already on a log scale. |
| `input_logged=False` | Apply `log2(value + 1)` before calculating differences. |
| `same_dir=True` | Preserve positive and negative changes for separate `greater` and `less` results. |
| `same_dir=False` | Use absolute changes when the question concerns magnitude rather than direction. |

Complete the normalization required by your expression workflow before this
step. The `input_logged=False` setting performs the stated
`log2(value + 1)` transformation.

Use the same planned direction setting when running the enrichment analysis.
For this standard fold-change workflow, leave the other preparation defaults
as `use_fold=True` and `rank_test=False`.
See {doc}`running GAGE <../guide/running>` for the analysis options.

## 5. Make the identifiers match

PyGAGE connects the measurement table to the gene sets by exact text:

```text
TP53               is not 7157
7157               is not ENSG00000141510
hsa:7157           is not 7157
```

Check how many gene-set members occur in the table:

```python
gene_sets = {
    "Example set": ["TP53", "BRCA1", "EGFR"],
}

measured_ids = set(expression["gene_id"].to_list())
gene_set_ids = {
    str(member)
    for members in gene_sets.values()
    for member in members
}

print("Measured IDs:", len(measured_ids))
print("Gene-set IDs:", len(gene_set_ids))
print("Matching IDs:", len(measured_ids & gene_set_ids))
```

The count should be biologically reasonable for the selected collection.
`set_size` in the final result reports how many unique members of each set were
found in the measurement table.

## 6. Convert gene symbols and Entrez IDs

PyGAGE 1.2.1 includes `GeneIDConverter`. Its default bundled mapping is the
human Entrez-ID-to-symbol map. This example adds converted Entrez IDs beside
the original gene symbols so the mapping can be reviewed first:

```python
import polars as pl

from pygage.gene_id_utils import GeneIDConverter


converter = GeneIDConverter()

conversion = converter.sym2eg(
    expression["gene_id"],
    as_frame=True,
)
print(conversion)

expression_with_ids = expression.with_columns(
    pl.Series(
        "entrez_id",
        conversion["output"].to_list(),
    )
)
print(
    expression_with_ids.select(
        ["gene_id", "entrez_id"]
    )
)
```

For the three example genes, the conversion table is:

| Input symbol | Entrez output |
| --- | --- |
| `TP53` | `7157` |
| `BRCA1` | `672` |
| `EGFR` | `1956` |

An unmatched symbol has a null value in the `output` or `entrez_id` column.
Review the table before replacing the original identifiers. Every gene used in
the next step should have the intended output identifier.

After reviewing how unmatched rows should be handled for the study, this
example keeps the mapped rows and creates an Entrez-ID analysis table:

```python
expression_entrez = (
    expression_with_ids
    .filter(pl.col("entrez_id").is_not_null())
    .drop("gene_id")
    .rename({"entrez_id": "gene_id"})
)
```

The reverse conversion uses:

```python
symbols = converter.eg2sym(
    ["7157", "672", "1956"]
)
print(symbols)
```

It returns:

```text
['TP53', 'BRCA1', 'EGFR']
```

For another species, supply a matching mapping file or build the corresponding
KEGG species map instead of using the bundled human map. See the gene-ID
conversion functions in the {doc}`API reference <../api>`.

## Preparation checklist

Before running a real analysis, confirm:

- one row represents one gene;
- the gene column is identified correctly;
- reference and sample positions exclude the gene column;
- the comparison design matches the experiment;
- the log-scale setting matches the input;
- measurement and gene-set IDs use the same system; and
- the prepared table has the expected number of comparison columns.

Continue with {doc}`inputs <../guide/inputs>`,
{doc}`gene-set sourcing <../guide/genesets>`, or
{doc}`running GAGE <../guide/running>`.

{doc}`Return to the beginner guide <index>`
