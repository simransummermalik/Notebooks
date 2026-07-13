# Make your first pathway

*Page 3 of 14*

On this page, you will color five genes on the human PI3K-Akt signaling
pathway. You will create two small Python files and then run one command.

## What you will make

Your finished image will be:

```text
pathview_output/hsa04151.first_pathway.png
```

The filename tells you what it contains:

- `hsa` means human;
- `04151` means PI3K-Akt signaling pathway; and
- `first_pathway` is the name of this run.

## 1. Create the reusable setup file

Open a code editor or plain-text editor. Create a blank file, paste the block
below, and save it inside `my-pathview-project` as exactly
`pathview_setup.py`.

```python
import importlib

from pathview.kegg_api import SpeciesInfo


def prepare_pathview():
    pathview_module = importlib.import_module("pathview.pathview")
    pathview_module.NODE_META_COLS = (
        pathview_module.NODE_META_COLS | {"bgcolor"}
    )

    def species_code_info(code):
        return SpeciesInfo(code, code != "ko", None, None, None, None)

    pathview_module.kegg_species_code = species_code_info
```

This is the standard setup helper used throughout the guide. It prepares KEGG
drawing information and passes your chosen species code into Pathview Plus.
Copy it once and leave it unchanged. Each pathway script will use it with two
simple lines:

```python
from pathview_setup import prepare_pathview

prepare_pathview()
```

Confirm that the filename ends in `.py`, not `.py.txt`.

## 2. Create the pathway script

Create another blank plain-text file in the same folder. Save it as
`first_pathway.py`, then paste this complete script:

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


# Run the standard setup from pathview_setup.py.
prepare_pathview()

# Make a table with Entrez Gene IDs and teaching values.
gene_data = pl.DataFrame(
    {
        "entrez_id": ["7157", "1956", "3845", "5290", "207"],
        "log2_fold_change": [-0.8, 0.9, 0.4, 0.6, 0.3],
    }
)

# Make a folder for the pathway files and finished image.
output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

# Place the values on the human PI3K-Akt pathway.
pathview(
    pathway_id="04151",
    species="hsa",
    gene_data=gene_data,
    gene_idtype="ENTREZ",
    map_symbol=False,
    kegg_dir=output_folder,
    kegg_native=True,
    output_format="png",
    out_suffix="first_pathway",
)

print("Finished! Open pathview_output/hsa04151.first_pathway.png")
```

## 3. Understand the imports

```python
from pathlib import Path
import polars as pl
from pathview import pathview
from pathview_setup import prepare_pathview
```

- `Path` helps Python create and name a folder.
- `polars as pl` gives the short name `pl` to the Polars table package.
- `pathview` is the function that creates the pathway image.
- `prepare_pathview` brings in the reusable setup from the first file.

This line runs that setup:

```python
prepare_pathview()
```

## 4. Understand the gene table

```python
gene_data = pl.DataFrame(
    {
        "entrez_id": ["7157", "1956", "3845", "5290", "207"],
        "log2_fold_change": [-0.8, 0.9, 0.4, 0.6, 0.3],
    }
)
```

This creates a two-column table inside Python:

| entrez_id | log2_fold_change |
| --- | ---: |
| 7157 | -0.8 |
| 1956 | 0.9 |
| 3845 | 0.4 |
| 5290 | 0.6 |
| 207 | 0.3 |

The first column tells Pathview Plus which genes to find. The second column
contains the numbers that become colors.

## 5. Understand the output folder

```python
output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)
```

The first line names the folder. The second line creates it. `exist_ok=True`
lets you run the script again using the same folder.

## 6. Understand the Pathview Plus settings

| Setting | Meaning in this example |
| --- | --- |
| `pathway_id="04151"` | choose the PI3K-Akt pathway |
| `species="hsa"` | choose human |
| `gene_data=gene_data` | use the table created above |
| `gene_idtype="ENTREZ"` | read the first column as Entrez IDs |
| `map_symbol=False` | use the direct ID mapping in this guide |
| `kegg_dir=output_folder` | save files in `pathview_output` |
| `kegg_native=True` | place colors on the KEGG pathway picture |
| `output_format="png"` | create a PNG image |
| `out_suffix="first_pathway"` | add `first_pathway` to the filename |

Pathview Plus uses its standard gene colors here: lower values move toward
green, values near zero move toward gray, and higher values move toward red.
Page 10 shows how to choose your own colors.

## 7. Run the script

Your project folder should now contain:

```text
my-pathview-project/
├── .venv/
├── pathview_setup.py
└── first_pathway.py
```

In Terminal, move into `my-pathview-project` and activate the virtual
environment as shown on page 2. Then run:

```bash
python first_pathway.py
```

## You are finished when

The script prints:

```text
Finished! Open pathview_output/hsa04151.first_pathway.png
```

Your folder will also contain the KEGG pathway files used to make the picture:

```text
pathview_output/
├── hsa04151.xml
├── hsa04151.png
└── hsa04151.first_pathway.png
```

Open the file with `first_pathway` in its name. You have made your first
Pathview Plus image.

[<- Previous: Install Pathview Plus](02-install.md) | [Home](../README.md) | [Next: Prepare your own data ->](04-prepare-your-data.md)
