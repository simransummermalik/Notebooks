# Run your first enrichment

*Page 3 of 31*

This page runs a complete PyGAGE analysis using a tiny practice dataset. You
will create one Python file and receive two CSV result files.

## What you will make

```text
pygage_output/
├── all_results.csv
└── significant_results.csv
```

The practice analysis contains:

- twelve genes;
- two already prepared measurement columns; and
- three teaching gene sets.

## 1. Create the script

Inside `my-pygage-project`, create a plain-text file named
`first_enrichment.py`.

Paste this complete script:

```python
from pathlib import Path

import polars as pl
from pygage import gage


# Each row is one gene. The two numeric columns are prepared changes.
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

# Run GAGE and receive one tidy result table.
result = gage(
    prepared_data,
    gene_sets,
    prepared=True,
    set_size_range=(2, 10),
)

# Keep rows passing a 0.05 q-value cutoff.
significant = (
    result
    .filter(pl.col("q_val") < 0.05)
    .sort("q_val")
)

# Create a folder and save both tables.
output_folder = Path("pygage_output")
output_folder.mkdir(exist_ok=True)

result.write_csv(output_folder / "all_results.csv")
significant.write_csv(
    output_folder / "significant_results.csv"
)

print("Significant teaching results:")
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

Confirm that the virtual environment is active. Then type:

```bash
python first_enrichment.py
```

## 3. Check the Terminal result

The significant table contains:

- `Growth pathway` in the `greater` direction; and
- `Stress pathway` in the `less` direction.

Small differences in the displayed decimal places can occur among Python
environments, while the same rows and directions remain the teaching result.

## 4. Open the saved files

Open:

```text
pygage_output/all_results.csv
```

This table contains all three gene sets in both directions.

Then open:

```text
pygage_output/significant_results.csv
```

This table contains the rows whose q-value is below `0.05`.

## Understand the imports

```python
from pathlib import Path
import polars as pl
from pygage import gage
```

| Import | Job |
| --- | --- |
| `Path` | creates and names the output folder |
| `polars as pl` | creates, filters, sorts, and saves tables |
| `gage` | runs the high-level PyGAGE workflow |

## Understand the measurement table

The table has this shape:

```text
gene_id | sample_change_1 | sample_change_2
```

- the first column contains gene identifiers;
- the second column contains one prepared comparison; and
- the third column contains another prepared comparison.

The first four genes have positive teaching values. Genes `7` through `10`
have negative teaching values.

## Understand the gene sets

```python
gene_sets = {
    "Growth pathway": ["1", "2", "3", "4"],
    "Stress pathway": ["7", "8", "9", "10"],
    "Mixed pathway": ["3", "5", "8", "11"],
}
```

A Python dictionary connects each set name to its member IDs:

```text
gene-set name -> list of gene IDs
```

The measurement table and gene sets both use the same text IDs.

## Understand the `gage()` call

```python
result = gage(
    prepared_data,
    gene_sets,
    prepared=True,
    set_size_range=(2, 10),
)
```

| Part | Meaning |
| --- | --- |
| `prepared_data` | use the teaching measurement table |
| `gene_sets` | test the three teaching groups |
| `prepared=True` | values are already gene-level changes |
| `set_size_range=(2, 10)` | include teaching sets with 2 through 10 matched genes |

Real analyses normally use the standard set-size range of 10 through 500.
The smaller range lets this twelve-gene example run.

## Understand the q-value filter

```python
significant = result.filter(
    pl.col("q_val") < 0.05
)
```

This keeps result rows whose multiple-testing-adjusted q-value is below the
teaching cutoff of `0.05`.

The cutoff is part of the analysis plan. Save it with the result.

## You are finished when

- Terminal prints the two significant teaching rows;
- `all_results.csv` exists;
- `significant_results.csv` exists; and
- both files open as tables.

[<- Previous: Install PyGAGE](02-install.md) | [Home](index.md) | [Next: Understand the first result ->](04-understand-enrichment.md)
