# Use a Jupyter notebook

*Page 25 of 31*

Use this page when you want to run PyGAGE one step at a time in a web browser.
A notebook is especially helpful while learning because code, explanations,
tables, and figures can stay in one document.

By the end of this page, you will have:

```text
my-pygage-project/
├── notebook_output/
│   ├── all_results.csv
│   └── significant_results.csv
└── pygage_notebook.ipynb
```

## Understand the three notebook parts

| Part | Meaning |
| --- | --- |
| notebook | the `.ipynb` file containing cells and saved output |
| cell | one editable section containing code or explanatory text |
| kernel | the Python process that runs the code and remembers variables |

A **code cell** runs Python. A **Markdown cell** displays headings, notes,
lists, and other formatted text.

The kernel remembers a variable only after the cell creating that variable has
run. This is why the order of notebook cells matters.

## 1. Open the project environment

Open Terminal and move into the project folder created on page 2.

On macOS or Linux:

```bash
cd my-pygage-project
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
cd my-pygage-project
.\.venv\Scripts\Activate.ps1
```

The environment is active when the Terminal line usually begins with:

```text
(.venv)
```

## 2. Install JupyterLab

Page 2 installs JupyterLab. If you have not installed it yet, run:

```bash
python -m pip install jupyterlab
```

Confirm that the command is available:

```bash
jupyter lab --version
```

The command prints the installed JupyterLab version.

## 3. Start JupyterLab

Keep the virtual environment active and run:

```bash
jupyter lab
```

JupyterLab starts a local server and normally opens in your web browser. The
files shown in its left sidebar belong to `my-pygage-project`.

Keep the Terminal window open while using the notebook. The Jupyter server is
running there.

## 4. Create and name the notebook

In the JupyterLab launcher:

1. select **Python 3** under **Notebook**;
2. choose **File**, then **Save Notebook As**;
3. enter `pygage_notebook.ipynb`; and
4. select **Save**.

Launching JupyterLab from the active `.venv` environment makes that
environment's PyGAGE installation available to the notebook.

## 5. Add a Markdown title cell

Select the first cell. Use the cell-type menu in the toolbar to change
**Code** to **Markdown**.

Enter:

```markdown
# My first PyGAGE notebook

This notebook runs a small, complete gene-set enrichment analysis.
```

Press **Shift+Enter**. JupyterLab formats the heading and moves to the next
cell.

## 6. Cell 1: import the tools and check PyGAGE

Make sure the next cell type is **Code**. Paste:

```python
from pathlib import Path

import polars as pl
import pygage
from pygage import gage
```

Press **Shift+Enter**.

Add another code cell and paste:

```python
print("PyGAGE version:", pygage.__version__)
```

Run it with **Shift+Enter**. The guide version prints:

```text
PyGAGE version: 1.2.1
```

The imports have these jobs:

| Import | Job |
| --- | --- |
| `Path` | creates the output folder and file paths |
| `polars as pl` | creates, filters, displays, and saves tables |
| `pygage` | provides the installed software version |
| `gage` | runs the high-level enrichment workflow |

## 7. Cell 2: create a prepared measurement table

Add a code cell and paste:

```python
prepared_data = pl.DataFrame(
    {
        "gene_id": [
            "1", "2", "3", "4", "5", "6",
            "7", "8", "9", "10", "11", "12",
        ],
        "sample_change_1": [
            2.4, 2.0, 1.8, 1.5, -0.2, 0.1,
            -1.8, -2.1, -1.5, -1.2, 0.3, -0.1,
        ],
        "sample_change_2": [
            2.2, 1.9, 1.6, 1.4, 0.0, 0.2,
            -1.7, -1.9, -1.4, -1.1, 0.2, 0.0,
        ],
    }
)

prepared_data
```

Run the cell. Because `prepared_data` is the final line, JupyterLab displays
the table directly below the cell.

Each row represents one gene. The two numeric columns contain prepared
gene-level changes.

## 8. Cell 3: create the teaching gene sets

Add and run this code cell:

```python
gene_sets = {
    "Growth pathway": ["1", "2", "3", "4"],
    "Stress pathway": ["7", "8", "9", "10"],
    "Mixed pathway": ["3", "5", "8", "11"],
}

print("Number of gene sets:", len(gene_sets))
```

The output is:

```text
Number of gene sets: 3
```

The identifiers in the lists match the text identifiers in
`prepared_data["gene_id"]`.

## 9. Cell 4: run PyGAGE

Add and run:

```python
result = gage(
    prepared_data,
    gene_sets,
    prepared=True,
    set_size_range=(2, 10),
)

result
```

This call means:

| Setting | Meaning |
| --- | --- |
| `prepared=True` | the numeric columns already contain gene-level changes |
| `set_size_range=(2, 10)` | test teaching sets with 2 through 10 matched genes |

The final `result` line displays the complete tidy result table.

## 10. Cell 5: keep the selected result rows

Add and run:

```python
significant = (
    result
    .filter(pl.col("q_val") < 0.05)
    .sort(["direction", "q_val"])
)

significant.select(
    [
        "gene_set",
        "direction",
        "set_size",
        "p_val",
        "q_val",
    ]
)
```

This displays the rows passing the teaching rule `q_val < 0.05`. Page 19
explains each result column.

## 11. Cell 6: save the tables

Add and run:

```python
output_folder = Path("notebook_output")
output_folder.mkdir(exist_ok=True)

result.write_csv(output_folder / "all_results.csv")
significant.write_csv(
    output_folder / "significant_results.csv"
)

print("Saved:", output_folder / "all_results.csv")
print("Saved:", output_folder / "significant_results.csv")
```

The left file browser will show `notebook_output`. If it does not appear
immediately, use the browser's refresh button.

The notebook and CSV files serve different purposes:

- the notebook records the code, notes, displayed tables, and run order; and
- the CSV files are portable result tables for later analysis or sharing.

## Run cells safely

The number beside a code cell shows its execution order:

```text
[1] first cell run
[2] second cell run
[*] cell currently running
```

Use these habits:

1. place imports near the top;
2. create data before using it;
3. run cells from top to bottom;
4. save important results to files; and
5. rerun the full notebook before treating it as complete.

## Restart and run the complete notebook

Restarting clears the kernel's memory. It checks that the notebook works from
the saved cells rather than from variables left over from earlier experiments.

In JupyterLab:

1. save the notebook;
2. open the **Kernel** menu;
3. select **Restart Kernel and Run All Cells**;
4. confirm the restart; and
5. read the cells from top to bottom to confirm every one completed.

After the restart, the first cell recreates the imports, later cells recreate
the data, and the final cell recreates the saved files.

If you choose **Restart Kernel** without running all cells, begin again with
the first code cell.

## Change a cell and rerun the analysis

For example, change the filtering line from:

```python
significant = result.filter(
    pl.col("q_val") < 0.05
)
```

to:

```python
significant = result.filter(
    pl.col("q_val") < 0.10
)
```

Then rerun that cell and the saving cell below it. Record the chosen rule in a
Markdown cell so the notebook explains the analysis decision.

## Save and close correctly

Use **File**, then **Save Notebook**, or press:

- **Command+S** on macOS; or
- **Ctrl+S** on Windows and Linux.

The `.ipynb` file stores code, Markdown text, and displayed output.

Closing a notebook tab does not necessarily stop its kernel. Use the
**Running** panel in JupyterLab to shut down the notebook kernel when finished.
Then return to Terminal and press **Ctrl+C** to stop the Jupyter server.

## Reopen the notebook later

Activate the same environment and start JupyterLab again:

```bash
cd my-pygage-project
source .venv/bin/activate
jupyter lab
```

On Windows PowerShell:

```powershell
cd my-pygage-project
.\.venv\Scripts\Activate.ps1
jupyter lab
```

Double-click `pygage_notebook.ipynb` in the file browser. Then use **Restart
Kernel and Run All Cells** to recreate the complete analysis.

## Notebook checklist

You are finished when:

- `pygage_notebook.ipynb` is saved;
- the version cell prints `1.2.1`;
- every cell runs from top to bottom after a kernel restart;
- the full and filtered tables display; and
- both CSV files exist inside `notebook_output`.

[<- Previous: Use the command line](24-command-line.md) | [Home](index.md) | [Next: Follow a real-data workflow ->](26-real-dataset.md)
