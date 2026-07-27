# Prepare your own data

*Page 4 of 24*

Pathview Plus reads a simple table. The first column contains identifiers. Each
later column contains numbers that you want to display as colors.

## Start with your analysis result

An analysis result is the table produced by your earlier statistical or
bioinformatics work. An annotation is descriptive information such as a gene
name or functional note.

Your full analysis table may contain gene names, identifiers, fold changes,
p-values, descriptions, and notes. Make a small Pathview table from it:

```text
identifier column + color-value column or columns
```

Keep p-values, gene names, and other annotations in your full analysis table so
you can use them when interpreting and reporting the result.

## One measurement column

This table displays one measurement for each gene:

| entrez_id | log2_fold_change |
| --- | ---: |
| 7157 | -1.8 |
| 1956 | 2.4 |
| 3845 | 1.1 |

The table shape is:

```text
ID | value
```

## Several measurement columns

This table displays three conditions for each gene:

| entrez_id | Control | Treatment_A | Treatment_B |
| --- | ---: | ---: | ---: |
| 1956 | 0.5 | 2.1 | 1.8 |
| 2099 | -0.3 | -1.5 | -0.9 |
| 5594 | 1.2 | 0.4 | 2.3 |

The table shape is:

```text
ID | first condition | second condition | third condition
```

Pathview Plus keeps the measurement columns in this order when it draws the
condition sections inside a mapped gene box.

## Choose the identifier system

Use one identifier system in the first column.

| Your data | First-column example | Setting used later |
| --- | --- | --- |
| genes with Entrez IDs | `1956` | `gene_idtype="ENTREZ"` |
| genes with symbols | `EGFR` | `gene_idtype="SYMBOL"` |
| genes with Ensembl IDs | `ENSG00000146648` | `gene_idtype="ENSEMBL"` |
| proteins with UniProt IDs | `P00533` | `gene_idtype="UNIPROT"` |
| KEGG Orthology data | `K02586` | `gene_idtype="KEGG"` |
| KEGG compounds | `C00031` | `cpd_idtype="KEGG"` |
| PubChem compounds | a PubChem compound ID | `cpd_idtype="PUBCHEM"` |
| ChEBI compounds | a ChEBI compound ID | `cpd_idtype="CHEBI"` |

Entrez IDs are the main gene identifiers used in this beginner guide. Many
analysis tools and annotation resources can add an Entrez ID column to a gene
result table. Pathview Plus can also convert the supported gene and compound
systems before it matches the pathway. Follow
[Convert gene and compound identifiers](16-identifier-conversion.md) for
complete examples.

## Save a TSV file

TSV means tab-separated values. It is a plain text table in which tabs separate
the columns.

In Excel, LibreOffice, or a similar spreadsheet program:

1. format the identifier column as **Text**;
2. place the identifiers in the first column;
3. place the values in the next column or columns;
4. put short column names in the first row;
5. choose **Save As**; and
6. choose **Tab-separated values (.tsv)** or **Text (Tab delimited)**.

Name a one-condition gene file `gene_data.tsv`. Its contents will look like:

```tsv
entrez_id	log2_fold_change
7157	-1.8
1956	2.4
3845	1.1
5290	1.5
207	0.9
```

## Load the TSV file with Polars

Place `gene_data.tsv` beside your Python script. Then use:

```python
import polars as pl

gene_data = pl.read_csv("gene_data.tsv", separator="\t").with_columns(
    pl.col("entrez_id").cast(pl.String)
)
```

Every part has a job:

- `pl.read_csv(...)` reads a text table into Python.
- `"gene_data.tsv"` is the filename.
- `separator="\t"` says that tabs separate the columns.
- `.with_columns(...)` prepares a column after reading it.
- `.cast(pl.String)` keeps identifiers as text.

You can print the table to see what Python read:

```python
print(gene_data)
```

## Create a table directly in Python

Small teaching examples can be written directly in a script:

```python
gene_data = pl.DataFrame(
    {
        "entrez_id": ["7157", "1956", "3845"],
        "log2_fold_change": [-1.8, 2.4, 1.1],
    }
)
```

The dictionary has one item for each column. The column name is on the left,
and its list of values is on the right.

## Choose a value that has a clear meaning

Write down four facts about every value column:

1. the column name;
2. what was measured or calculated;
3. the comparison or condition; and
4. the units or scale.

For example:

```text
Column: log2_fold_change
Meaning: log2 expression fold change
Comparison: treated samples versus control samples
Scale: zero is unchanged; positive is higher; negative is lower
```

These facts will become part of the pathway figure caption.

## Data checklist

Before continuing, confirm that:

- the first column contains one type of identifier;
- identifiers are stored as text;
- every later column contains numbers;
- the headers are short and meaningful;
- the species matches the identifiers; and
- you know what positive, zero, and negative values mean in your analysis.

[<- Previous: Make your first pathway](03-first-pathway.md) | [Home](index.md) | [Next: Choose a pathway and species ->](05-choose-a-pathway.md)
