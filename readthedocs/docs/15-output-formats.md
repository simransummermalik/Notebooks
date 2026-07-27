# Choose PNG, SVG, or PDF output

*Page 15 of 24*

Use this page when you need to choose an image format for a report,
presentation, poster, manuscript, or later editing.

Pathview Plus 2.0.2 can write three finished-image formats:

- **PNG** places the data colors on the familiar KEGG pathway picture;
- **SVG** redraws the mapped pathway nodes as a scalable vector image; and
- **PDF** draws the pathway as a scalable graph.

## Start with the recommended combinations

These three setting pairs make the requested format and drawing style clear:

| Finished file | Settings | Drawing style | A good choice for |
| --- | --- | --- | --- |
| PNG | `kegg_native=True`, `output_format="png"` | data over the KEGG pathway picture | first checks, slides, web pages, and familiar KEGG figures |
| SVG | `kegg_native=False`, `output_format="svg"` | vector nodes at pathway coordinates | scaling and editing in a vector graphics program |
| PDF | `kegg_native=False`, `output_format="pdf"` | vector graph view | manuscripts, posters, and printable figures |

PNG is a pixel image. SVG and PDF are vector formats, so lines, shapes, and
text remain sharp when the figure is enlarged.

## Understand how Pathview Plus chooses a renderer

The `pathview()` function uses the settings in this order:

| Request | Renderer used | Finished extension |
| --- | --- | --- |
| `output_format="svg"` | SVG renderer | `.svg` |
| `output_format="png"` and `kegg_native=True` | KEGG native renderer | `.png` |
| all other format and native-setting combinations | graph renderer | `.pdf` |

Use the recommended pairs in the first table when you want the filename
extension to match the format named in your script.

## Understand native, SVG, and graph views

| View | What Pathview Plus draws | Pathway source files used |
| --- | --- | --- |
| KEGG native PNG | the KEGG pathway picture with colored gene and compound regions | the pathway PNG and KGML XML |
| SVG | colored vector nodes using positions stored in KGML | the pathway KGML XML |
| PDF graph | pathway nodes as a directed graph at KGML positions | the pathway KGML XML |

The scientific input values and color settings can stay the same across all
three views. Only the way the finished pathway is drawn changes.

## Make all three formats

Create `make_output_formats.py` inside `my-pathview-project`. Keep
`pathview_setup.py` from page 3 in the same folder.

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

gene_data = pl.DataFrame(
    {
        "entrez_id": ["7157", "1956", "3845", "5290", "207"],
        "log2_fold_change": [-1.8, 2.4, 1.1, 1.5, 0.9],
    }
)

output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

common_settings = {
    "pathway_id": "04151",
    "species": "hsa",
    "gene_data": gene_data,
    "gene_idtype": "ENTREZ",
    "map_symbol": False,
    "kegg_dir": output_folder,
    "limit": {"gene": 2.5, "cpd": 1.0},
    "low": {"gene": "#2166AC", "cpd": "blue"},
    "mid": {"gene": "#F7F7F7", "cpd": "gray"},
    "high": {"gene": "#B2182B", "cpd": "yellow"},
}

# Familiar KEGG picture with a data overlay.
pathview(
    **common_settings,
    kegg_native=True,
    output_format="png",
    out_suffix="report_png",
    new_signature=True,
    plot_col_key=True,
)

# Scalable SVG pathway.
pathview(
    **common_settings,
    kegg_native=False,
    output_format="svg",
    out_suffix="report_svg",
    new_signature=True,
)

# Scalable PDF graph.
pathview(
    **common_settings,
    kegg_native=False,
    output_format="pdf",
    out_suffix="report_pdf",
    new_signature=True,
    plot_col_key=True,
)

print("Finished! Open the three report files in pathview_output.")
```

Run the script:

```bash
python make_output_formats.py
```

## Find the finished files

The three calls create:

```text
pathview_output/
├── hsa04151.report_png.png
├── hsa04151.report_svg.svg
└── hsa04151.report_pdf.pdf
```

Pathview Plus also keeps the downloaded pathway source files in the same
folder:

```text
hsa04151.xml
hsa04151.png
```

The source PNG is named `hsa04151.png`. The finished data-colored PNG contains
the suffix and is named `hsa04151.report_png.png`.

## Understand the filename

Every finished filename follows this pattern:

```text
species + pathway number + output suffix + extension
```

For example:

```text
hsa04151.report_png.png
```

| Part | Meaning |
| --- | --- |
| `hsa` | human species code |
| `04151` | PI3K-Akt signaling pathway |
| `report_png` | value supplied to `out_suffix` |
| `.png` | finished image format |

Choose a short suffix that identifies the analysis, such as:

```python
out_suffix="treatment_vs_control"
```

Use letters, numbers, and underscores so filenames remain easy to read and
share.

## Choose whether to show the signature

```python
new_signature=True
```

This adds the Pathview Plus rendering signature to the finished figure. It is
the default. To make the figure without that line, use:

```python
new_signature=False
```

The setting applies to PNG, SVG, and PDF output.

## Choose whether to show the color key

```python
plot_col_key=True
```

The color key connects pathway colors to the numeric scale. It is shown by
the PNG and PDF renderers when this setting is `True`.

To make a PNG or PDF without the color key, use:

```python
plot_col_key=False
```

The SVG renderer creates the scalable pathway drawing without a color-key
panel. Keep the exact `limit`, `low`, `mid`, and `high` settings with the SVG,
and explain the scale in its caption or a separate legend.

## Choose a format for publication

Check the figure instructions for the journal, conference, thesis, or poster.
Then choose the matching output:

- use **PNG** when the instructions request a raster image or when the KEGG
  picture is the preferred view;
- use **SVG** when you need a scalable file for a vector editor; or
- use **PDF** when the instructions accept a vector PDF and the graph view fits
  the figure.

For a final scientific figure:

1. keep the original Pathview Plus output;
2. keep the script and input table that created it;
3. record the pathway ID, species, identifier type, and software version;
4. use the same color limits across figures that will be compared;
5. state the meaning and units of every color scale; and
6. confirm that labels remain readable at the final printed size.

## Quick format checklist

Before sharing a figure, confirm:

- the filename contains a meaningful suffix;
- the chosen format opens in the program that will use it;
- the pathway ID and species are correct;
- the color key or caption explains the numeric values;
- the figure caption describes the comparison; and
- the script, input table, and original output are saved together.

[<- Previous: Glossary](14-glossary.md) | [Home](index.md) | [Next: Convert identifiers ->](16-identifier-conversion.md)
