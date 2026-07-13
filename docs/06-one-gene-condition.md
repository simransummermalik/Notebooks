# Map one gene measurement

*Page 6 of 14*

Use this workflow when every gene has one number to display. You will read a
TSV file and color six genes on the human cell-cycle pathway.

## What you will make

```text
pathview_output/hsa04110.cell_cycle.png
```

## What you need

- the Pathview Plus project from page 3;
- `pathview_setup.py` inside that project;
- one TSV file with Entrez Gene IDs and values; and
- one new Python script.

## 1. Create the input file

Create `cell_cycle_genes.tsv` inside `my-pathview-project`:

```tsv
entrez_id	log2_fold_change
7157	-0.8
595	0.6
1017	0.9
1019	0.4
5925	-0.5
1869	0.7
```

The first column contains Entrez Gene IDs. The second column contains one log2
fold-change value for each gene.

## 2. Create the script

Create `cell_cycle.py` in the same folder and paste this code:

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

# Read the tab-separated gene table.
gene_data = pl.read_csv(
    "cell_cycle_genes.tsv",
    separator="\t",
).with_columns(
    pl.col("entrez_id").cast(pl.String)
)

# Make the output folder.
output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

# Draw the values on the human cell-cycle pathway.
pathview(
    pathway_id="04110",
    species="hsa",
    gene_data=gene_data,
    gene_idtype="ENTREZ",
    map_symbol=False,
    kegg_dir=output_folder,
    kegg_native=True,
    output_format="png",
    out_suffix="cell_cycle",
)

print("Finished! Open pathview_output/hsa04110.cell_cycle.png")
```

## 3. Understand the data-loading lines

```python
gene_data = pl.read_csv(
    "cell_cycle_genes.tsv",
    separator="\t",
).with_columns(
    pl.col("entrez_id").cast(pl.String)
)
```

- `pl.read_csv(...)` reads the table into Python.
- `"cell_cycle_genes.tsv"` is the input filename.
- `separator="\t"` says that tabs separate the columns.
- `pl.col("entrez_id")` selects the first column by name.
- `.cast(pl.String)` keeps each identifier as text.

The resulting Polars DataFrame is named `gene_data`.

## 4. Understand the pathway choices

```python
pathway_id="04110"
species="hsa"
gene_idtype="ENTREZ"
```

Together, these settings mean:

```text
Place my Entrez Gene values on the human cell-cycle pathway.
```

These lines choose the output:

```python
kegg_dir=output_folder
kegg_native=True
output_format="png"
out_suffix="cell_cycle"
```

They save a KEGG pathway picture as
`pathview_output/hsa04110.cell_cycle.png`.

## 5. Run the workflow

Your folder should contain all three files:

```text
my-pathview-project/
├── pathview_setup.py
├── cell_cycle_genes.tsv
└── cell_cycle.py
```

In Terminal, move into `my-pathview-project`, activate `.venv`, and run:

```bash
python cell_cycle.py
```

## You are finished when

Open:

```text
pathview_output/hsa04110.cell_cycle.png
```

The mapped cell-cycle genes will be colored from green through gray to red
according to their log2 fold-change values.

## Reuse this workflow with your data

Change these pieces everywhere they appear:

| Teaching piece | Replace with |
| --- | --- |
| `cell_cycle_genes.tsv` | your TSV filename |
| `entrez_id` | your first-column header |
| `log2_fold_change` | your value-column header |
| `04110` and `hsa` | your pathway number and species code |
| `cell_cycle` | a short name for your analysis |

This recipe uses Entrez Gene IDs. For KO IDs that begin with `K`, continue to
[Map KEGG Orthology data](08-kegg-orthology.md). For compound IDs that begin
with `C`, continue to
[Map compounds and multi-omics data](09-compounds-and-multiomics.md).

[<- Previous: Choose a pathway and species](05-choose-a-pathway.md) | [Home](../README.md) | [Next: Compare several gene conditions ->](07-multiple-gene-conditions.md)
