# Highlight a finished pathway

*Page 21 of 24*

Use this page when you already have a Pathview Plus PNG and want to emphasize
selected genes, connections, or an ordered path.

Highlighting is an advanced post-processing workflow. You first make the
pathway with `pathview()`, then place its image and mapped node tables inside a
`PathwayResult`.

## What the highlighting tools do

| Tool | Result |
| --- | --- |
| `PathwayResult` | keeps the image, mapped tables, and added layers together |
| `highlight_nodes()` | draws borders around selected mapped nodes |
| `highlight_edges()` | draws lines between selected mapped gene coordinates |
| `highlight_path()` | highlights an ordered list of nodes and consecutive connections |
| `change_labels()` | records replacement labels for a custom rendering step |

Use six-digit hex colors such as `"#D73027"`. This makes color input explicit
and repeatable.

## 1. Make the base pathway

The complete example below uses the setup helper created on
[page 3](03-first-pathway.md). Save it as `highlight_pathway.py` in the same
project folder as `pathview_setup.py`.

```python
from pathlib import Path

import numpy as np
import polars as pl
from PIL import Image
from pathview import (
    PathwayResult,
    highlight_edges,
    highlight_nodes,
    highlight_path,
    pathview,
)

from pathview_setup import prepare_pathview


prepare_pathview()

gene_data = pl.DataFrame(
    {
        "entrez_id": ["7157", "1956", "3845", "5290", "207"],
        "log2_fold_change": [-0.8, 0.9, 0.4, 0.6, 0.3],
    }
)

output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

base = pathview(
    pathway_id="04151",
    species="hsa",
    gene_data=gene_data,
    gene_idtype="ENTREZ",
    map_symbol=False,
    kegg_dir=output_folder,
    kegg_native=True,
    output_format="png",
    out_suffix="highlight_base",
)
```

`base` is the dictionary returned by `pathview()`. It contains the mapped node
tables under `"plot_data_gene"` and `"plot_data_cpd"`.

## 2. Prepare the IDs used by the highlighting tools

The highlighting functions match the exact strings in a column named
`kegg_names`. The high-level KEGG result can store one or more prefixed IDs in
the `name` column, so this small function makes one clean ID per row.

Add this code below the first block:

```python
def normalize_kegg_names(table):
    if table is None or "kegg_names" in table.columns:
        return table

    return (
        table
        .with_columns(
            pl.col("name").str.split(" ").alias("kegg_names")
        )
        .explode("kegg_names")
        .with_columns(
            pl.col("kegg_names")
            .str.strip_chars()
            .str.replace(r"^[a-z]+:", "")
            .alias("kegg_names")
        )
        .filter(pl.col("kegg_names") != "")
    )


plot_gene = normalize_kegg_names(base["plot_data_gene"])
plot_cpd = normalize_kegg_names(base["plot_data_cpd"])
```

For example, `hsa:1956` becomes `1956`. Exploding the list also lets a pathway
box with several IDs be matched by any one of those IDs.

## 3. Inspect the available IDs

Always inspect the mapped IDs before selecting a highlight:

```python
print(
    plot_gene
    .select(["kegg_names", "label", "x", "y"])
    .unique()
    .sort("kegg_names")
)
```

Copy highlight IDs from the printed `kegg_names` column. This keeps the
highlighting step connected to the exact pathway result you just made.

## 4. Create a `PathwayResult`

Continue the script:

```python
base_image_path = (
    output_folder / "hsa04151.highlight_base.png"
)

result = PathwayResult(
    pathway_id="hsa04151",
    plot_data_gene=plot_gene,
    plot_data_cpd=plot_cpd,
    output_path=base_image_path,
    image_array=np.array(
        Image.open(base_image_path).convert("RGB")
    ),
)
```

The fields have separate jobs:

| Field | Purpose |
| --- | --- |
| `pathway_id` | names the pathway represented by the result |
| `plot_data_gene` | supplies mapped gene IDs and coordinates |
| `plot_data_cpd` | supplies mapped compound IDs and coordinates |
| `output_path` | records the base image location |
| `image_array` | holds editable RGB pixels |

## 5. Add node and edge highlights

The `+` operator adds one layer at a time and returns a new
`PathwayResult`.

```python
highlighted = (
    result
    + highlight_nodes(
        ["1956", "5290"],
        color="#D73027",
        width=4,
    )
    + highlight_edges(
        [("1956", "5290")],
        color="#2166AC",
        width=3,
    )
)

highlighted.save(
    output_folder / "hsa04151.highlighted.png"
)
```

In this example:

- `highlight_nodes()` draws a red border around the two mapped gene boxes;
- `highlight_edges()` draws a blue line from the first supplied gene
  coordinate to the second; and
- `save()` writes the modified RGB image as a PNG.

You supply each edge as a `(source_id, target_id)` pair. This makes the intended
connection explicit in the script.

## 6. Highlight an ordered path

`highlight_path()` is a shortcut for highlighting nodes plus the lines between
each consecutive pair.

```python
ordered_path = (
    result
    + highlight_path(
        ["1956", "5290", "207"],
        color="#FDAE61",
        node_width=4,
        edge_width=3,
    )
)

ordered_path.save(
    output_folder / "hsa04151.ordered_path.png"
)
```

The list order defines these pairs:

```text
1956 -> 5290
5290 -> 207
```

Use an order that represents the sequence you want the figure to emphasize.

## 7. Record label replacements

`change_labels()` stores requested label substitutions on the composed result.
Those substitutions are metadata for a later custom rendering step.

```python
from pathview import change_labels


labeled = (
    result
    + change_labels(
        {
            "1956": "EGFR",
            "5290": "PIK3CA",
        },
        font_size=11,
        color="#000000",
    )
)

print(labeled._label_changes)
```

Borders and connecting lines are the immediately visible raster layers.
Stored label metadata can be read by a custom text-rendering workflow.

## Function reference

```python
highlight_nodes(
    node_ids,
    color="red",
    width=4,
    opacity=1.0,
)

highlight_edges(
    edge_pairs,
    color="blue",
    width=3,
)

highlight_path(
    path_node_ids,
    color="orange",
    node_width=3,
    edge_width=2,
)

change_labels(
    label_map,
    font_size=11,
    color="black",
)
```

`PathwayResult.save(path, format="png")` can save PNG output. Passing
`format="pdf"` saves the edited raster image inside a PDF.

## Before saving a final figure

Confirm that:

- every selected ID appears in the inspected `kegg_names` table;
- the path list is in the intended order;
- each color is a six-digit hex value;
- the base image and highlighted image have different filenames; and
- the caption explains what each border or line means biologically.

[<- Previous: Work with SBGN and other databases](20-sbgn-and-databases.md) | [Home](index.md) | [Next: Build custom curves and SVG elements ->](22-curves-and-svg.md)
