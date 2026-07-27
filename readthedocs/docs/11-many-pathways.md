# Run several pathways

*Page 11 of 24*

Use a Python loop when you want to place the same gene table on several
pathways.

## What you will make

One script will create three images:

```text
many_pathway_results/hsa04110.cell_cycle.png
many_pathway_results/hsa04010.mapk_signaling.png
many_pathway_results/hsa04151.pi3k_akt_signaling.png
```

## What is a loop?

A loop tells Python to repeat the same action for every item in a group.

Here, the group contains three pathway numbers. The repeated action is the
`pathview()` call.

## 1. Create the script

Create `many_pathways.py` inside `my-pathview-project`. Keep
`pathview_setup.py` in the same folder.

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

# Make one table for all three pathways.
gene_data = pl.DataFrame(
    {
        "entrez_id": [
            "1956", "5594", "5595", "5604", "5605",
            "2885", "3845", "7157", "1026", "1019",
            "1021", "5925", "5290", "207", "5728",
        ],
        "log2_fold_change": [
            0.8, -0.4, 0.6, -0.6, 0.3,
            0.5, -0.7, 0.9, 0.6, -0.4,
            0.3, -0.7, 0.8, 0.4, -0.6,
        ],
    }
)

# Connect each pathway number to a short output name.
pathways = {
    "04110": "cell_cycle",
    "04010": "mapk_signaling",
    "04151": "pi3k_akt_signaling",
}

output_folder = Path("many_pathway_results")
output_folder.mkdir(exist_ok=True)

# Run the same Pathview Plus call once for each pathway.
for pathway_id, short_name in pathways.items():
    print(f"Making {short_name}...")

    pathview(
        pathway_id=pathway_id,
        species="hsa",
        gene_data=gene_data,
        gene_idtype="ENTREZ",
        map_symbol=False,
        kegg_dir=output_folder,
        kegg_native=True,
        output_format="png",
        out_suffix=short_name,
    )

print("Finished! Open the many_pathway_results folder.")
```

## 2. Understand the pathway dictionary

```python
pathways = {
    "04110": "cell_cycle",
    "04010": "mapk_signaling",
    "04151": "pi3k_akt_signaling",
}
```

A Python dictionary connects one item to another. Each line connects:

```text
pathway number -> short output name
```

The short names become the filename suffixes.

## 3. Understand the loop line

```python
for pathway_id, short_name in pathways.items():
    ...
```

- `for` starts a loop.
- `.items()` gives the loop each number-and-name pair from the dictionary.
- `pathway_id` receives the current pathway number.
- `short_name` receives its matching output name.
- the colon starts the indented block that will repeat.

## 4. Understand the changing settings

Inside the loop, these values change during every pass:

```python
pathway_id=pathway_id
out_suffix=short_name
```

The first pass uses `04110` and `cell_cycle`. The second uses `04010` and
`mapk_signaling`. The third uses `04151` and `pi3k_akt_signaling`.

Every other setting stays the same, including the gene table and human species
code.

## 5. Understand the indentation

The `pathview()` call is indented beneath the `for` line. Indentation tells
Python which action belongs inside the loop.

```python
for pathway_id, short_name in pathways.items():
    pathview(
        pathway_id=pathway_id,
        # the other settings stay here
    )
```

## 6. Run the script

In Terminal, move into `my-pathview-project`, activate `.venv`, and run:

```bash
python many_pathways.py
```

## You are finished when

Terminal prints:

```text
Finished! Open the many_pathway_results folder.
```

Open the folder and then open each filename listed at the beginning of this
page.

## Use your own pathway list

Change only the dictionary:

```python
pathways = {
    "04110": "my_cell_cycle_result",
    "04512": "my_ecm_result",
}
```

Keep every pathway number inside quotes. Give every pathway a different short
name so each image receives a different filename.

## Use pathway IDs from an enrichment table

An enrichment program may produce a table containing pathway IDs and adjusted
p-values. You can filter that table first and then give each selected pathway
to the same loop.

Suppose `enriched_pathways.tsv` contains:

| pathway_id | pathway_name | adjusted_p_value |
| --- | --- | ---: |
| 04110 | Cell cycle | 0.004 |
| 04010 | MAPK signaling pathway | 0.018 |
| 04151 | PI3K-Akt signaling pathway | 0.031 |

Read the pathway IDs as strings so leading zeroes are preserved:

```python
enrichment = pl.read_csv(
    "enriched_pathways.tsv",
    separator="\t",
    schema_overrides={"pathway_id": pl.String},
)

selected_pathways = (
    enrichment
    .filter(pl.col("adjusted_p_value") < 0.05)
    .get_column("pathway_id")
    .drop_nulls()
    .unique()
    .to_list()
)

for pathway_id in selected_pathways:
    pathview(
        pathway_id=pathway_id,
        species="hsa",
        gene_data=gene_data,
        gene_idtype="ENTREZ",
        map_symbol=False,
        kegg_dir=output_folder,
        out_suffix=f"enrichment_{pathway_id}",
    )
```

The enrichment table chooses the pathways. The gene table still supplies the
values that become colors. Record the enrichment cutoff and the source of the
gene values with the finished figures.

[<- Previous: Choose colors and read the image](10-colors-and-images.md) | [Home](index.md) | [Next: Use Pathview Plus in a notebook ->](12-use-a-notebook.md)
