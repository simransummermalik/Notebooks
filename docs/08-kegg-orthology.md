# Map KEGG Orthology data

*Page 8 of 14*

Use this workflow when the first column of your results contains KEGG
Orthology identifiers, also called KO IDs.

## What you will make

You will color KO values on the nitrogen-metabolism reference pathway:

```text
pathview_output/ko00910.ko_nitrogen.png
```

## What is a KO ID?

A KO ID represents a biological function shared across organisms. It begins
with a capital `K` followed by five digits, such as `K02586`.

KO data uses these two Pathview Plus settings:

```python
species="ko"
gene_idtype="KEGG"
```

`ko` selects the KEGG Orthology reference pathway. `KEGG` tells Pathview Plus
that the first column contains KEGG identifiers.

## 1. Understand the input

| ko_id | difference |
| --- | ---: |
| K02586 | 0.72 |
| K02588 | -0.34 |
| K00370 | 0.18 |
| K00371 | -0.61 |

The first column contains KO IDs. The second column contains one numeric result
for each KO.

## 2. Create the script

Create `ko_nitrogen.py` inside `my-pathview-project`. Keep
`pathview_setup.py` in the same folder.

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

ko_data = pl.DataFrame(
    {
        "ko_id": ["K02586", "K02588", "K00370", "K00371"],
        "difference": [0.72, -0.34, 0.18, -0.61],
    }
)

output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

pathview(
    pathway_id="00910",
    species="ko",
    gene_data=ko_data,
    gene_idtype="KEGG",
    map_symbol=False,
    kegg_dir=output_folder,
    kegg_native=True,
    output_format="png",
    out_suffix="ko_nitrogen",
)

print("Finished! Open pathview_output/ko00910.ko_nitrogen.png")
```

## 3. Understand the table name

```python
ko_data = pl.DataFrame(...)
```

`ko_data` is the Python name for the table. It is passed through the
`gene_data` argument because Pathview Plus uses that argument for both organism
genes and KO functions:

```python
gene_data=ko_data
```

## 4. Understand the pathway name

```python
pathway_id="00910"
species="ko"
```

The pathway number is `00910`, including both leading zeroes. Pathview Plus
combines it with `ko` to make the full pathway name `ko00910`.

## 5. Run the script

In Terminal, move into `my-pathview-project`, activate `.venv`, and run:

```bash
python ko_nitrogen.py
```

## You are finished when

Open:

```text
pathview_output/ko00910.ko_nitrogen.png
```

The matching KO boxes will be colored according to the `difference` column.

## Use your own KO data

You can replace the inline table with a TSV file:

```python
ko_data = pl.read_csv(
    "my_ko_data.tsv",
    separator="\t",
).with_columns(
    pl.col("ko_id").cast(pl.String)
)
```

Then replace the pathway ID, filename, value-column name, and output suffix with
the choices for your analysis.

[<- Previous: Compare several gene conditions](07-multiple-gene-conditions.md) | [Home](../README.md) | [Next: Map compounds and multi-omics data ->](09-compounds-and-multiomics.md)
