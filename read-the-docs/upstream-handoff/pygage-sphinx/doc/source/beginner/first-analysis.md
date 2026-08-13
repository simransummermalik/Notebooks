# Run your first analysis

This practice analysis uses a tiny dataset created inside one Python script.
It is designed to teach the workflow before you prepare real files.

By the end, you will have:

```text
pygage_output/
├── all_results.csv
└── significant_results.csv
```

## Before you start

Complete the official {doc}`installation instructions <../installation>`, then
open Terminal or PowerShell in a folder where you want to keep the practice
files.

## 1. Create the script

Create a plain-text file named `first_enrichment.py` and paste this complete
example:

```python
from pathlib import Path

import polars as pl
from pygage import gage


# Each row is one gene. The numeric columns are prepared gene-level changes.
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

# Each name is connected to a list of member gene IDs.
gene_sets = {
    "Growth pathway": ["1", "2", "3", "4"],
    "Stress pathway": ["7", "8", "9", "10"],
    "Mixed pathway": ["3", "5", "8", "11"],
}

# Run PyGAGE and receive one tidy result table.
result = gage(
    prepared_data,
    gene_sets,
    prepared=True,
    set_size_range=(2, 10),
)

# Keep rows passing the teaching q-value rule.
significant = (
    result
    .filter(pl.col("q_val") < 0.05)
    .sort("q_val")
)

# Create an output folder and save both tables.
output_folder = Path("pygage_output")
output_folder.mkdir(exist_ok=True)

result.write_csv(output_folder / "all_results.csv")
significant.write_csv(
    output_folder / "significant_results.csv"
)

print(
    significant.select(
        [
            "gene_set",
            "direction",
            "set_size",
            "p_val",
            "q_val",
        ]
    )
)
print("Finished! Open the pygage_output folder.")
```

## 2. Run the script

Type:

```bash
python first_enrichment.py
```

The selected result contains two rows:

| Gene set | Direction | Matched genes | Approximate q-value |
| --- | --- | ---: | ---: |
| Growth pathway | `greater` | 4 | 0.029 |
| Stress pathway | `less` | 4 | 0.033 |

The two CSV files will appear inside `pygage_output`.

## 3. Understand each part

### The measurement table

Each row represents one gene. The first four genes have positive values in
both prepared columns, while genes `7` through `10` have negative values.

### The gene sets

A Python dictionary connects each set name to its member IDs:

```text
gene-set name -> list of gene IDs
```

The IDs are text in both the measurement table and the gene sets.

### The `gage()` call

| Setting | Meaning |
| --- | --- |
| `prepared=True` | The numeric columns already contain gene-level changes. |
| `set_size_range=(2, 10)` | Test teaching sets with 2 through 10 matched members. |

Real analyses normally use the default range of 10 through 500 matched genes.
The smaller range is only for this twelve-gene example.

### The result

PyGAGE asks two directional questions for each gene set:

- Does the set tend toward higher or more positive values? (`greater`)
- Does the set tend toward lower or more negative values? (`less`)

The `Growth pathway` genes are consistently positive, so that set appears in
the `greater` direction. The `Stress pathway` genes are consistently negative,
so that set appears in the `less` direction.

`set_size` is the number of unique set members found in the measurement table.
The `q_val` column adjusts for testing multiple gene sets. This example keeps
rows with `q_val < 0.05`.

```{note}
The names and numbers in this practice dataset were created for teaching. A
real biological interpretation also needs a documented study design,
appropriate preprocessing, matching identifiers, and a relevant gene-set
collection.
```

## Where to go next

- Use {doc}`prepare your data <prepare-data>` for a raw expression matrix.
- Read {doc}`understanding the results <../guide/results>` for the complete
  result-column definitions.
- Try the official {doc}`quickstart <../quickstart>` for the packaged real-data
  example.
- Read {doc}`how GAGE works <../method>` when you want the statistical details.

{doc}`Return to the beginner guide <index>`
