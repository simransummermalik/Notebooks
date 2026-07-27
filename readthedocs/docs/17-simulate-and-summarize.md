# Simulate data and summarize repeated mappings

*Page 17 of 24*

Use this page when you want practice data, need to combine repeated
measurements, or want to inspect the tables returned by Pathview Plus.

The tools on this page have three different jobs:

| Tool or setting | Job |
| --- | --- |
| `sim_mol_data()` | create a practice gene or compound table |
| `mol_sum()` | combine rows by using an ID mapping table |
| `node_sum` | choose how repeated values are combined during pathway mapping |

## Part A: Create practice data

Import the simulation function with:

```python
from pathview import sim_mol_data
```

Its complete call is:

```python
sim_mol_data(
    mol_type="gene",
    species="hsa",
    n_mol=100,
    n_exp=1,
    rand_seed=100,
    discrete=False,
)
```

## Understand every simulation setting

| Setting | Default | Meaning |
| --- | ---: | --- |
| `mol_type` | `"gene"` | make `"gene"` IDs or `"cpd"` compound IDs |
| `species` | `"hsa"` | KEGG organism code used to select gene IDs |
| `n_mol` | `100` | number of molecules to include |
| `n_exp` | `1` | number of numeric experiment columns |
| `rand_seed` | `100` | repeatable starting point for random sampling |
| `discrete` | `False` | include numeric values; use `True` for an ID-only table |

Gene simulation retrieves gene IDs for the selected KEGG species. Compound
simulation creates KEGG-style compound IDs such as `C00001`.

## Make a two-condition gene table

Create `practice_data.py`:

```python
from pathview import sim_mol_data


gene_data = sim_mol_data(
    mol_type="gene",
    species="hsa",
    n_mol=200,
    n_exp=2,
    rand_seed=42,
    discrete=False,
)

print(gene_data.head())
print(gene_data.shape)
```

Run it:

```bash
python practice_data.py
```

The table has this shape:

| id | exp1 | exp2 |
| --- | ---: | ---: |
| a selected human gene ID | a simulated value | a simulated value |
| another selected human gene ID | a simulated value | a simulated value |

The exact IDs come from the selected species. `rand_seed=42` lets the same
simulation setup be repeated. The experiment columns are named `exp1`,
`exp2`, and so on.

## Make a compound table

```python
from pathview import sim_mol_data


compound_data = sim_mol_data(
    mol_type="cpd",
    n_mol=50,
    n_exp=3,
    rand_seed=7,
)

print(compound_data.head())
```

This creates:

```text
id | exp1 | exp2 | exp3
```

The first column contains compound IDs. The other three columns contain
simulated numeric measurements.

## Make an ID-only table

Use `discrete=True` when you need only a sampled list of identifiers:

```python
gene_ids = sim_mol_data(
    mol_type="gene",
    species="hsa",
    n_mol=25,
    discrete=True,
)

print(gene_ids)
```

The result has one column:

```text
id
```

Because it has no numeric value column, this form is useful for practicing ID
selection. Use `discrete=False` for the tables that will become pathway
colors.

## Draw a pathway with simulated gene data

Create `simulated_pathway.py` inside `my-pathview-project`:

```python
from pathlib import Path

from pathview import pathview, sim_mol_data

from pathview_setup import prepare_pathview


prepare_pathview()

gene_data = sim_mol_data(
    mol_type="gene",
    species="hsa",
    n_mol=500,
    n_exp=2,
    rand_seed=100,
)

output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

result = pathview(
    pathway_id="04151",
    species="hsa",
    gene_data=gene_data,
    gene_idtype="ENTREZ",
    map_symbol=False,
    kegg_dir=output_folder,
    kegg_native=True,
    output_format="png",
    out_suffix="simulated_two_conditions",
    node_sum="sum",
)

print("Finished! Open:")
print("pathview_output/hsa04151.simulated_two_conditions.png")
```

Simulated values are for learning the workflow. Use measurements from your
completed analysis when making a biological result.

## Combine repeated identifiers

Sometimes several source IDs point to the same final gene or compound ID.
`mol_sum()` joins a measurement table to an ID mapping table and combines the
rows for each final ID.

Its complete call is:

```python
mol_sum(mol_data, id_map, sum_method="sum")
```

The two input tables are:

1. `mol_data`: source IDs in the first column and numeric values after them;
2. `id_map`: source IDs in the first column and final IDs in the second.

## Run a complete summarizing example

```python
import polars as pl
from pathview import mol_sum


measurements = pl.DataFrame(
    {
        "probe_id": ["probe_A", "probe_B", "probe_C"],
        "condition_1": [2.0, -1.0, 0.5],
        "condition_2": [1.0, 3.0, 2.0],
    }
)

id_map = pl.DataFrame(
    {
        "source_id": ["probe_A", "probe_B", "probe_C"],
        "entrez_id": ["1956", "1956", "5290"],
    }
)

summed = (
    mol_sum(measurements, id_map, sum_method="sum")
    .rename({"probe_id": "entrez_id"})
    .sort("entrez_id")
)

print(summed)
```

The two rows that map to `1956` are added:

| entrez_id | condition_1 | condition_2 |
| --- | ---: | ---: |
| 1956 | 1.0 | 4.0 |
| 5290 | 0.5 | 2.0 |

For `1956`, the calculation is:

```text
condition_1: 2.0 + (-1.0) = 1.0
condition_2: 1.0 + 3.0 = 4.0
```

The output keeps the numeric column names from the measurement table. The
example renames its first column to `entrez_id` so the final identifier system
is clear.

## Choose a summary method

Both `mol_sum(..., sum_method=...)` and
`pathview(..., node_sum=...)` accept these choices:

| Choice | What it returns for a repeated group |
| --- | --- |
| `"sum"` | the values added together |
| `"mean"` | the arithmetic average |
| `"median"` | the middle value |
| `"max"` | the largest numeric value |
| `"max_abs"` | the original value with the largest absolute size |
| `"random"` | one randomly selected value |

For example, the values `-4.0`, `1.0`, and `3.0` produce:

| Method | Result |
| --- | ---: |
| `sum` | `0.0` |
| `mean` | `0.0` |
| `median` | `1.0` |
| `max` | `3.0` |
| `max_abs` | `-4.0` |

Choose the method that matches the meaning of your data and record it with the
analysis. `sum` is the Pathview Plus default.

## Understand `node_sum`

Use the selected method inside `pathview()`:

```python
result = pathview(
    pathway_id="04151",
    species="hsa",
    gene_data=gene_data,
    gene_idtype="ENTREZ",
    node_sum="mean",
)
```

`node_sum` is used when several input IDs or measurements map to one pathway
node. Every numeric condition column is summarized separately.

Examples:

- use `sum` for values that should be added;
- use `mean` when each contributing row should have equal weight;
- use `median` for the middle contributing measurement; or
- use `max_abs` when the strongest positive or negative measurement should
  represent the node.

## Part C: Inspect the returned result tables

`pathview()` returns a dictionary with two possible Polars DataFrames:

| Dictionary key | Contents |
| --- | --- |
| `"plot_data_gene"` | gene-node positions, labels, and mapped gene values |
| `"plot_data_cpd"` | compound-node positions, labels, and mapped compound values |

Capture the dictionary instead of discarding it:

```python
result = pathview(
    pathway_id="04151",
    species="hsa",
    gene_data=gene_data,
    gene_idtype="ENTREZ",
    map_symbol=False,
    kegg_dir="pathview_output",
    out_suffix="inspect_tables",
)

gene_nodes = result["plot_data_gene"]
compound_nodes = result["plot_data_cpd"]

if gene_nodes is not None:
    print(gene_nodes.head())
    print(gene_nodes.columns)

if compound_nodes is not None:
    print(compound_nodes.head())
```

A plot-data table can include:

- `entry_id`: the pathway node ID;
- `name` or `kegg_names`: identifiers connected to the node;
- `label`: the pathway label;
- `x`, `y`, `width`, and `height`: drawing information; and
- your numeric experiment columns, such as `exp1` and `exp2`.

You can save a returned table for review:

```python
if gene_nodes is not None:
    gene_nodes.write_csv(
        "pathview_output/hsa04151.inspect_tables.gene_nodes.tsv",
        separator="\t",
    )
```

## Part D: Control pathway mapping

Three settings help describe how nodes are prepared.

### `map_symbol`

```python
map_symbol=True
```

For Entrez gene data, `True` requests gene-symbol labels. Use `False` when you
want to keep the direct identifier-based pathway labels used in the beginner
examples:

```python
map_symbol=False
```

### `map_null`

```python
map_null=True
```

This is the default. It keeps a position-only pathway layer when a gene or
compound table is not supplied for that layer. Use:

```python
map_null=False
```

when you want an unsupplied data layer omitted.

### `min_nnodes`

```python
min_nnodes=3
```

This is the default minimum number of pathway nodes available for mapping.
For a small teaching pathway, you can choose a different minimum:

```python
min_nnodes=1
```

Record a changed minimum with the analysis so another researcher can repeat
the same pathway selection.

## Reproducibility checklist

When simulation or summarizing is part of a workflow, save:

- the `rand_seed` used for simulated data;
- the `mol_type`, species, molecule count, and experiment count;
- the ID mapping table used by `mol_sum()`;
- the selected `sum_method` or `node_sum`;
- the returned gene or compound plot-data table; and
- the complete script that produced the result.

[<- Previous: Convert identifiers](16-identifier-conversion.md) | [Home](index.md) | [Next: Use the command line ->](18-command-line.md)
