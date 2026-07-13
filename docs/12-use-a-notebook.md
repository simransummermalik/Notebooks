# Use Pathview Plus in a notebook

*Page 12 of 14*

A Jupyter notebook lets you run Python in small sections called cells. This
page divides one complete Pathview Plus workflow into five cells.

## What you will make

```text
pathview_output/hsa04110.notebook_cell_cycle.png
```

## 1. Install and open JupyterLab

In Terminal, move into `my-pathview-project` and activate `.venv`. Install
JupyterLab once:

```bash
python -m pip install jupyterlab
```

Start it from the same project folder:

```bash
python -m jupyter lab
```

JupyterLab opens in your web browser. Choose **File**, **New**, and
**Notebook**. Select the Python kernel and name the file
`cell_cycle_notebook.ipynb`.

A kernel is the Python environment that runs the notebook cells. Choose the
kernel connected to the `.venv` environment where Pathview Plus is installed.

## How to run a cell

1. Click inside the cell.
2. Press **Shift + Enter**.
3. Wait for a number to appear beside the cell.

Run the following cells in order from Cell 1 through Cell 5.

## 2. Cell 1: load the tools

Copy and run:

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview

prepare_pathview()
```

This cell loads the folder tool, Polars, Pathview Plus, and the standard helper
you created on page 3.

## 3. Cell 2: make the gene table

Copy and run:

```python
gene_data = pl.DataFrame(
    {
        "entrez_id": ["7157", "595", "1017", "1019", "5925", "1869"],
        "log2_fold_change": [-0.8, 0.6, 0.9, 0.4, -0.5, 0.7],
    }
)

gene_data
```

The last line displays the table directly below the cell.

## 4. Cell 3: make the output folder

Copy and run:

```python
output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)
```

This creates `pathview_output` beside the notebook.

## 5. Cell 4: make the pathway image

Copy and run:

```python
pathview(
    pathway_id="04110",
    species="hsa",
    gene_data=gene_data,
    gene_idtype="ENTREZ",
    map_symbol=False,
    kegg_dir=output_folder,
    kegg_native=True,
    output_format="png",
    out_suffix="notebook_cell_cycle",
)
```

This cell uses the table from Cell 2 and the folder from Cell 3. It places the
values on the human cell-cycle pathway.

## 6. Cell 5: print the image name

Copy and run:

```python
print("Open pathview_output/hsa04110.notebook_cell_cycle.png")
```

Use JupyterLab's file browser to open that PNG.

## Why the order matters

Each cell prepares something used later:

1. Cell 1 loads the tools.
2. Cell 2 creates `gene_data`.
3. Cell 3 creates `output_folder`.
4. Cell 4 uses both names to run Pathview Plus.
5. Cell 5 reminds you which image to open.

## You are finished when

The image opens from the JupyterLab file browser and its mapped cell-cycle
genes contain your colors.

## Run the notebook with new values

1. Change the IDs or values in Cell 2.
2. Change `pathway_id`, `species`, or `out_suffix` in Cell 4.
3. Choose **Run**, then **Run All Cells**.
4. Open the new PNG from `pathview_output`.

Save the notebook when you finish. It keeps the code, input table, and order of
the pathway workflow together.

[<- Previous: Run several pathways](11-many-pathways.md) | [Home](../README.md) | [Next: Recipe book ->](13-recipe-book.md)
