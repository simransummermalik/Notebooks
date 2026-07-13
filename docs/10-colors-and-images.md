# Choose colors and read the image

*Page 10 of 14*

This page shows how to choose a low color, a middle color, a high color, and a
numeric limit.

## What you will make

```text
pathview_output/hsa04151.blue_white_red.png
```

The gene values will use a blue-white-red scale.

## 1. Understand the three colors

For a measurement centered at zero:

| Part of scale | Gene color | Meaning for this example |
| --- | --- | --- |
| low | blue | negative log2 fold change |
| middle | white | log2 fold change near zero |
| high | red | positive log2 fold change |

The biological meaning comes from the value column. Write its name, units, and
comparison in the figure caption.

## 2. Understand hex color codes

A hex color code is a precise six-character color label that begins with `#`.
For example:

| Code | Color |
| --- | --- |
| `#2166AC` | blue |
| `#F7F7F7` | near-white |
| `#B2182B` | red |

You can also use common color names such as `"blue"`, `"white"`, and
`"red"`.

## 3. Create the script

Create `custom_colors.py` inside `my-pathview-project`. Keep
`pathview_setup.py` in the same folder.

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

gene_data = pl.DataFrame(
    {
        "entrez_id": ["1956", "5290", "207", "5728", "2475"],
        "log2_fold_change": [2.4, 1.5, 0.8, -1.3, -2.1],
    }
)

output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

pathview(
    pathway_id="04151",
    species="hsa",
    gene_data=gene_data,
    gene_idtype="ENTREZ",
    map_symbol=False,
    kegg_dir=output_folder,
    kegg_native=True,
    output_format="png",
    out_suffix="blue_white_red",
    plot_col_key=True,
    limit={"gene": 2.0, "cpd": 1.0},
    low={"gene": "#2166AC", "cpd": "blue"},
    mid={"gene": "#F7F7F7", "cpd": "gray"},
    high={"gene": "#B2182B", "cpd": "yellow"},
)

print("Finished! Open pathview_output/hsa04151.blue_white_red.png")
```

## 4. Understand the color settings

```python
low={"gene": "#2166AC", "cpd": "blue"}
mid={"gene": "#F7F7F7", "cpd": "gray"}
high={"gene": "#B2182B", "cpd": "yellow"}
```

Each color setting contains both Pathview Plus data types:

- `gene` chooses the gene color; and
- `cpd` chooses the compound color.

This script sends only gene data, so the blue-white-red gene choices appear on
the pathway. Keeping both keys makes each color setting complete.

## 5. Understand the limit

```python
limit={"gene": 2.0, "cpd": 1.0}
```

The gene scale runs from `-2.0` to `2.0`:

| Value | Gene color area |
| ---: | --- |
| `-2.0` or lower | strongest blue |
| `-1.0` | lighter blue |
| `0` | white |
| `1.0` | lighter red |
| `2.0` or higher | strongest red |

Values beyond the two ends use the endpoint color. Choose a limit that fits
the units and spread of your measurement, then use the same limit when figures
will be compared directly.

## 6. Understand the color key

```python
plot_col_key=True
```

This draws the numeric gene color scale below the pathway. Readers can use it
to connect the colors to the log2 fold-change values.

## 7. Run the script

In Terminal, move into `my-pathview-project`, activate `.venv`, and run:

```bash
python custom_colors.py
```

## You are finished when

Open:

```text
pathview_output/hsa04151.blue_white_red.png
```

The output folder also contains `hsa04151.png`, the KEGG pathway picture saved
for the run. The filename with `blue_white_red` is your finished data-colored
image.

## What to record with the image

Save these details with every final figure:

- Pathview Plus version;
- pathway number and species code;
- identifier type;
- value-column meaning and units;
- low, middle, and high colors;
- numeric limits; and
- input table and script filename.

[<- Previous: Map compounds and multi-omics data](09-compounds-and-multiomics.md) | [Home](../README.md) | [Next: Run several pathways ->](11-many-pathways.md)
