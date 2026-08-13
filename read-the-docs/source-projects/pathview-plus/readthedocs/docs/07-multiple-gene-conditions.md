# Compare several gene conditions

*Page 7 of 24*

Use this workflow when the same genes have values from several conditions,
treatments, samples, or time points.

## What you will make

You will make one human MAPK signaling pathway for three conditions:

1. `Control`
2. `Treatment_A`
3. `Treatment_B`

Each mapped gene box will contain three color sections in that same order.

## 1. Understand the table shape

The first column contains Entrez Gene IDs. Every later column contains one set
of values.

| entrez_id | Control | Treatment_A | Treatment_B |
| --- | ---: | ---: | ---: |
| 1956 | 0.2 | 0.9 | 0.7 |
| 3845 | -0.3 | 0.5 | -0.2 |
| 5604 | 0.1 | -0.4 | 0.6 |
| 5594 | -0.4 | 0.2 | 0.8 |

Use the same kind of measurement in every condition column. For example, all
three columns could contain log2 fold changes calculated in the same way.

## 2. Create the script

Create `multiple_conditions.py` inside `my-pathview-project`. Keep
`pathview_setup.py` in the same folder.

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

# Put IDs first, followed by conditions in display order.
gene_data = pl.DataFrame(
    {
        "entrez_id": ["1956", "3845", "5604", "5594"],
        "Control": [0.2, -0.3, 0.1, -0.4],
        "Treatment_A": [0.9, 0.5, -0.4, 0.2],
        "Treatment_B": [0.7, -0.2, 0.6, 0.8],
    }
)

output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

pathview(
    pathway_id="04010",
    species="hsa",
    gene_data=gene_data,
    gene_idtype="ENTREZ",
    map_symbol=False,
    kegg_dir=output_folder,
    kegg_native=True,
    output_format="png",
    out_suffix="three_conditions",
)

print("Finished! Open pathview_output/hsa04010.three_conditions.png")
```

## 3. Understand the condition columns

```python
gene_data = pl.DataFrame(
    {
        "entrez_id": ["1956", "3845", "5604", "5594"],
        "Control": [0.2, -0.3, 0.1, -0.4],
        "Treatment_A": [0.9, 0.5, -0.4, 0.2],
        "Treatment_B": [0.7, -0.2, 0.6, 0.8],
    }
)
```

Each list becomes one DataFrame column. The order in the script is also the
left-to-right order inside each mapped gene box:

```text
Control | Treatment_A | Treatment_B
  left        middle          right
```

Record those condition names in the same order with your saved input and figure
caption.

## 4. Understand the pathway settings

```python
pathway_id="04010"
species="hsa"
```

`04010` selects MAPK signaling, and `hsa` selects human.

```python
out_suffix="three_conditions"
```

The suffix gives the result this filename:

```text
hsa04010.three_conditions.png
```

## 5. Run the script

In Terminal, move into `my-pathview-project`, activate `.venv`, and run:

```bash
python multiple_conditions.py
```

## You are finished when

Open:

```text
pathview_output/hsa04010.three_conditions.png
```

The mapped MAPK gene boxes will contain three left-to-right color sections.

## Use a TSV file instead

For a real dataset, save the same four-column shape as
`multiple_conditions.tsv`, then replace the `pl.DataFrame(...)` section with:

```python
gene_data = pl.read_csv(
    "multiple_conditions.tsv",
    separator="\t",
).with_columns(
    pl.col("entrez_id").cast(pl.String)
)
```

Add or remove numeric columns to match the conditions you want to display.

[<- Previous: Map one gene measurement](06-one-gene-condition.md) | [Home](index.md) | [Next: Map KEGG Orthology data ->](08-kegg-orthology.md)
