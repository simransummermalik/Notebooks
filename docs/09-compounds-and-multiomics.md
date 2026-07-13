# Map compounds and multi-omics data

*Page 9 of 14*

This page starts with compounds by themselves. It then adds genes and compounds
to the same pathway image.

## Part A: map compounds

A KEGG compound ID begins with a capital `C` followed by five digits. For
example, `C00031` identifies glucose.

### What you will make

```text
pathview_output/hsa00010.compounds.png
```

This example uses the human Glycolysis / Gluconeogenesis pathway.

### 1. Understand the compound table

| compound_id | log2_fold_change |
| --- | ---: |
| C00031 | 0.8 |
| C00118 | -0.6 |
| C00022 | 0.9 |

The first column contains KEGG compound IDs. The second contains the numeric
values that become colors.

### 2. Create the compound script

Create `compounds.py` inside `my-pathview-project`. Keep
`pathview_setup.py` in the same folder.

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

compound_data = pl.DataFrame(
    {
        "compound_id": ["C00031", "C00118", "C00022"],
        "log2_fold_change": [0.8, -0.6, 0.9],
    }
)

output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

pathview(
    pathway_id="00010",
    species="hsa",
    cpd_data=compound_data,
    cpd_idtype="KEGG",
    map_symbol=False,
    map_null=False,
    plot_col_key=False,
    kegg_dir=output_folder,
    kegg_native=True,
    output_format="png",
    out_suffix="compounds",
)

print("Finished! Open pathview_output/hsa00010.compounds.png")
```

### 3. Understand the compound settings

```python
cpd_data=compound_data
cpd_idtype="KEGG"
```

- `cpd_data` is the Pathview Plus argument for a compound table.
- `compound_data` is the Python name you gave that table.
- `cpd_idtype="KEGG"` describes the `C` identifiers in its first column.

The compound-only recipe also uses:

```python
map_null=False
plot_col_key=False
```

These settings focus the run and image on the compound measurements you
provided. Lower compound values move toward blue, values near zero move toward
gray, and higher values move toward yellow.

### 4. Run the compound script

In Terminal, move into `my-pathview-project`, activate `.venv`, and run:

```bash
python compounds.py
```

Open `pathview_output/hsa00010.compounds.png`. The mapped compound shapes will
show the values from `compound_data`.

## Part B: map genes and compounds together

When one experiment has gene results and compound results, prepare two tables
and pass both tables to one `pathview()` call.

### What you will make

```text
pathview_output/hsa00010.genes_and_compounds.png
```

### 1. Understand the two tables

Gene table:

| entrez_id | log2_fold_change |
| --- | ---: |
| 3098 | 0.8 |
| 3099 | -0.5 |
| 2821 | 0.4 |
| 3939 | -0.7 |

Compound table:

| compound_id | log2_fold_change |
| --- | ---: |
| C00031 | 0.8 |
| C00118 | -0.6 |
| C00022 | 0.9 |

Both tables follow the same rule: identifiers are first and numeric values are
second.

### 2. Create the combined script

Create `genes_and_compounds.py`:

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

gene_data = pl.DataFrame(
    {
        "entrez_id": ["3098", "3099", "2821", "3939"],
        "log2_fold_change": [0.8, -0.5, 0.4, -0.7],
    }
)

compound_data = pl.DataFrame(
    {
        "compound_id": ["C00031", "C00118", "C00022"],
        "log2_fold_change": [0.8, -0.6, 0.9],
    }
)

output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

pathview(
    pathway_id="00010",
    species="hsa",
    gene_data=gene_data,
    cpd_data=compound_data,
    gene_idtype="ENTREZ",
    cpd_idtype="KEGG",
    map_symbol=False,
    kegg_dir=output_folder,
    kegg_native=True,
    output_format="png",
    out_suffix="genes_and_compounds",
)

print(
    "Finished! Open "
    "pathview_output/hsa00010.genes_and_compounds.png"
)
```

### 3. Understand the two data arguments

```python
gene_data=gene_data
cpd_data=compound_data
```

The first line sends the Entrez gene table. The second sends the KEGG compound
table. Both are placed on `hsa00010` during one run.

```python
gene_idtype="ENTREZ"
cpd_idtype="KEGG"
```

These settings describe the first column in each table.

### 4. Run the combined script

In Terminal:

```bash
python genes_and_compounds.py
```

## You are finished when

Open:

```text
pathview_output/hsa00010.genes_and_compounds.png
```

The mapped gene boxes use the gene scale, and the mapped compound shapes use
the compound scale. You now have both data types on one pathway.

[<- Previous: Map KEGG Orthology data](08-kegg-orthology.md) | [Home](../README.md) | [Next: Choose colors and read the image ->](10-colors-and-images.md)
