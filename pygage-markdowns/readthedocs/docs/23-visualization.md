# Make enrichment plots

*Page 23 of 31*

Use this page to turn PyGAGE results and gene-level values into saved image
files. The examples save PNG files, so they work in a script, notebook, remote
session, or Read the Docs-style workflow.

## Choose the plot for the question

| Question | PyGAGE plot |
| --- | --- |
| Which gene sets have the strongest evidence and statistics? | bubble plot |
| How do gene-set statistics compare across conditions? | enrichment heatmap |
| Where do one set's members occur in a ranked gene list? | running-enrichment plot |
| What are the fold changes of one set's member genes? | gene-color grid |
| What pattern do selected genes show across samples? | regular or clustered heatmap |
| How similar are one reference and sample column? | scatterplot |
| How many hits are shared across two or three conditions? | Venn diagram on Page 22 |

## Install the plotting dependencies

The source installation on Page 2 installs the standard plotting packages:

```text
matplotlib
seaborn
```

If you installed a custom minimal environment, add them with:

```bash
python -m pip install matplotlib seaborn
```

## Create every main plot

Create `make_pygage_plots.py`:

```python
from pathlib import Path

from matplotlib import cm, colormaps
import polars as pl
from pygage.visualization_utils import (
    ColorUtils,
    EnrichmentPlots,
    HeatmapPlotter,
)
from pygage.data_processing_utils import GeneDataExporter


output_folder = Path("pygage_plots")
output_folder.mkdir(exist_ok=True)

# Keep the color-grid call consistent across Matplotlib releases.
if not hasattr(cm, "get_cmap"):
    cm.get_cmap = colormaps.get_cmap

# Practice enrichment results for two conditions.
condition_a = pl.DataFrame(
    {
        "gene_set": [
            "Protein processing",
            "Oxidative phosphorylation",
            "Proteasome",
            "Cell cycle",
        ],
        "set_size": [144, 97, 39, 82],
        "stat_mean": [4.8, 3.9, 3.3, -2.1],
        "q_val": [1.0e-12, 2.0e-8, 4.0e-6, 0.02],
    }
)

condition_b = pl.DataFrame(
    {
        "gene_set": [
            "Protein processing",
            "Oxidative phosphorylation",
            "Proteasome",
            "Cell cycle",
        ],
        "set_size": [142, 96, 40, 80],
        "stat_mean": [2.2, -2.8, 1.5, 3.4],
        "q_val": [2.0e-4, 7.0e-7, 0.03, 5.0e-6],
    }
)

# 1. Bubble plot for one result table.
EnrichmentPlots.bubble_plot(
    condition_a,
    top_n=4,
    title="Condition A enriched gene sets",
    output_file=output_folder / "01_bubble_plot.png",
)

# 2. Heatmap comparing result statistics across conditions.
EnrichmentPlots.enrichment_heatmap(
    {
        "condition_a": condition_a,
        "condition_b": condition_b,
    },
    value="stat_mean",
    top_n=4,
    output_file=output_folder / "02_enrichment_heatmap.png",
    title="Enrichment across conditions",
)

# Practice pre-ranked gene table.
ranked = pl.DataFrame(
    {
        "gene_id": [
            "G1", "G2", "G3", "G4", "G5", "G6",
            "G7", "G8", "G9", "G10", "G11", "G12",
        ],
        "score": [
            3.5, 3.0, 2.6, 1.8, 1.0, 0.4,
            -0.2, -0.8, -1.4, -2.0, -2.8, -3.2,
        ],
    }
)

selected_set = ["G1", "G2", "G4", "G8"]

# 3. Running-enrichment view for one ranked set.
running_summary = EnrichmentPlots.running_enrichment(
    ranked,
    gene_set=selected_set,
    gene_col="gene_id",
    score_col="score",
    weight=1.0,
    title="Example set in the ranked list",
    output_file=output_folder / "03_running_enrichment.png",
)

print("Running-enrichment summary:")
print(running_summary)

# 4. Gene-color grid and reusable gene-to-color dictionary.
fold_changes = {
    "G1": 2.7,
    "G2": 1.9,
    "G4": 0.8,
    "G8": -1.4,
}

gene_colors = EnrichmentPlots.pathway_gene_colors(
    pathway_genes=selected_set,
    fold_changes=fold_changes,
    title="Example set member changes",
    vmax=3.0,
    output_file=output_folder / "04_gene_color_grid.png",
)

print("Gene colors:")
print(gene_colors)

# Practice gene-by-sample values.
expression = pl.DataFrame(
    {
        "gene_id": ["G1", "G2", "G3", "G4", "G5"],
        "control_1": [5.1, 3.2, 7.0, 2.4, 4.0],
        "control_2": [5.3, 3.0, 6.8, 2.6, 4.1],
        "treated_1": [8.2, 5.0, 6.7, 3.8, 2.9],
        "treated_2": [8.0, 5.2, 6.9, 3.7, 3.0],
    }
)

sample_columns = [
    "control_1",
    "control_2",
    "treated_1",
    "treated_2",
]

# 5. Standard heatmap.
HeatmapPlotter.plot_heatmap(
    expression.select(sample_columns),
    row_labels=expression["gene_id"].to_list(),
    col_labels=sample_columns,
    cmap="RdBu_r",
    center=None,
    output_file=output_folder / "05_expression_heatmap.png",
    title="Selected-gene expression",
)

# 6. Clustered heatmap.
HeatmapPlotter.plot_clustered_heatmap(
    expression,
    gene_col="gene_id",
    cmap="RdBu_r",
    output_file=output_folder / "06_clustered_heatmap.png",
    title="Clustered selected-gene expression",
)

# 7. Reference-versus-sample scatterplot.
GeneDataExporter.create_scatterplot(
    expression_data=expression,
    ref_col="control_1",
    samp_col="treated_1",
    gene_col="gene_id",
    genes=None,
    output_file=output_folder / "07_scatterplot.png",
    title="Control 1 versus treated 1",
)

# 8. Create PyGAGE colormaps for later plot calls.
blue_white_red = ColorUtils.create_colormap(
    low="blue",
    mid="white",
    high="red",
    n=256,
)

green_black_red = ColorUtils.greenred(
    n=256,
)

print("Custom colormaps created:")
print(blue_white_red.name)
print(green_black_red.name)
print("Finished! Open the pygage_plots folder.")
```

Run:

```bash
python make_pygage_plots.py
```

The output folder will contain:

```text
pygage_plots/
├── 01_bubble_plot.png
├── 02_enrichment_heatmap.png
├── 03_running_enrichment.png
├── 04_gene_color_grid.png
├── 05_expression_heatmap.png
├── 06_clustered_heatmap.png
└── 07_scatterplot.png
```

The small `cm` compatibility block near the top gives PyGAGE the same named
colormap lookup across current Matplotlib releases. Leave those lines in the
script when making the gene-color grid.

## Read the bubble plot

The default bubble plot maps:

| Visual property | Result column |
| --- | --- |
| horizontal position | `stat_mean` |
| color | `-log10(q_val)` |
| bubble size | `set_size` |
| row label | `gene_set` |

Larger `-log10(q_val)` means a smaller q-value. The function selects the
`top_n` rows after sorting by q-value.

For a tidy table containing both directions, filter one direction first:

```python
greater = result.filter(
    pl.col("direction") == "greater"
)

EnrichmentPlots.bubble_plot(
    greater,
    top_n=20,
    output_file=Path("greater_bubble.png"),
)
```

## Read the enrichment heatmap

The heatmap has:

- gene sets in rows;
- conditions in columns; and
- the selected result value in each cell.

The standard `value="stat_mean"` uses a red/blue scale centered at zero.
PyGAGE forms the row list from the union of the top results in each condition,
so a pathway can appear even when it is not among the top results everywhere.

Use one direction consistently in every condition:

```python
results_by_condition = {
    "untreated": untreated_tables["greater"],
    "treated": treated_tables["greater"],
}
```

## Read the running-enrichment plot

The plot:

- orders genes from the largest score to the smallest;
- places a small mark wherever a set member occurs;
- increases the running value at a hit;
- decreases it at a miss; and
- marks the strongest absolute point.

The function returns:

```python
{
    "ES": enrichment_score,
    "leading_edge": leading_gene_ids,
    "n_hits": matched_member_count,
}
```

`weight=1.0` weights hits by the absolute score. Use the same planned weight
when comparing plots.

## Read the PyGAGE gene-color grid

`pathway_gene_colors()` maps each supplied member's fold change to a color and
saves a compact labeled grid. It also returns:

```text
gene ID -> hexadecimal color
```

For example:

```python
print(gene_colors["G1"])
```

may print a value shaped like:

```text
#b1182b
```

An ID without a supplied fold change is shown in gray. Use `vmax` to apply the
same symmetric color limits across several figures.

## Choose a regular or clustered heatmap

Use `HeatmapPlotter.plot_heatmap()` when the existing row and column order
should stay fixed.

Use `HeatmapPlotter.plot_clustered_heatmap()` when the figure should arrange
similar row and column patterns together.

For a gene table, provide `gene_col="gene_id"` so the labels are separated
from the numeric matrix.

## Use a custom colormap

Create a two-color scale:

```python
two_color = ColorUtils.create_colormap(
    low="navy",
    mid=None,
    high="gold",
)
```

Create a three-color scale:

```python
three_color = ColorUtils.create_colormap(
    low="blue",
    mid="white",
    high="red",
)
```

`ColorUtils.greenred()` supplies PyGAGE's green-black-red scale. The returned
Matplotlib colormap can be passed as `cmap=` to compatible plotting functions:

```python
HeatmapPlotter.plot_heatmap(
    expression.select(sample_columns),
    row_labels=expression["gene_id"].to_list(),
    col_labels=sample_columns,
    cmap=three_color,
    output_file=Path("custom_heatmap.png"),
)
```

## Make figures reproducible

Keep these details:

- the exact result or gene table;
- the filtering rule and direction;
- the plot function and arguments;
- PyGAGE version;
- figure file name;
- color limits such as `vmin`, `vmax`, or `center`; and
- the script or notebook that created the image.

Use the same limits and result columns when comparing figures.

[<- Previous: Filter, group, compare, and export](22-group-overlap.md) | [Home](index.md) | [Next: Use the command line ->](24-command-line.md)
