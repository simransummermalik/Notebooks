# Follow a real-data workflow

*Page 26 of 31*

Use this page when you are ready to move from the twelve-gene teaching example
to a complete analysis of real biological data.

PyGAGE 1.2.1 includes a prepared version of the GAGE `gse16873` demonstration
dataset and matching KEGG gene sets. The analysis on this page works from the
files inside the installed package, so it needs no database download.

## What the dataset represents

The original expression study contains:

- 11,979 measured genes;
- six head-and-neck, or HN, samples; and
- six ductal carcinoma in situ, or DCIS, samples.

The packaged prepared table contains six paired comparison columns. Each
column represents the change for one DCIS sample relative to its paired HN
sample:

```text
gene_id | DCIS_1 | DCIS_2 | DCIS_3 | DCIS_4 | DCIS_5 | DCIS_6
```

Because the comparisons are already prepared, the analysis uses:

```python
prepared=True
```

## What PyGAGE provides

The installed package contains:

| File | Contents |
| --- | --- |
| `gse16873_prepared.csv.gz` | 11,979 gene rows and six prepared comparison columns |
| `kegg_gs.json` | 177 human KEGG gene sets |

The `.gz` ending means the CSV is compressed. Polars reads it directly, so it
does not need to be uncompressed manually.

## What you will create

```text
my-pygage-project/
├── gse16873_analysis.py
└── gse16873_results/
    ├── all_results.csv
    ├── significant_results.csv
    ├── top_greater_results.csv
    ├── greater_bubble.png
    └── analysis_record.txt
```

## 1. Create the analysis script

Inside `my-pygage-project`, create `gse16873_analysis.py`.

Paste this complete script:

```python
import json
import platform
import sys
from pathlib import Path

import polars as pl
import pygage
from pygage import core, gage
from pygage.visualization_utils import EnrichmentPlots


# Locate the data inside the installed PyGAGE package.
package_folder = Path(core.__file__).resolve().parent
regression_folder = package_folder / "data" / "regression"

prepared_path = (
    regression_folder / "gse16873_prepared.csv.gz"
)
gene_sets_path = regression_folder / "kegg_gs.json"

# Read gene identifiers as text and load the gene-set dictionary.
prepared = pl.read_csv(
    prepared_path,
    schema_overrides={"gene_id": pl.Utf8},
)
gene_sets = json.loads(
    gene_sets_path.read_text(encoding="utf-8")
)

# Confirm what was loaded before starting the analysis.
print("Prepared table shape:", prepared.shape)
print("Prepared columns:", prepared.columns)
print("Number of gene sets:", len(gene_sets))

# Run the standard one-call workflow on prepared data.
result = gage(
    prepared,
    gene_sets,
    prepared=True,
)

# Select useful result views.
significant = (
    result
    .filter(pl.col("q_val") < 0.05)
    .sort(["direction", "q_val"])
)

greater = (
    result
    .filter(pl.col("direction") == "greater")
    .sort("p_val")
)

top_greater = greater.head(20)

# Create the output folder and save the tables.
output_folder = Path("gse16873_results")
output_folder.mkdir(exist_ok=True)

result.write_csv(output_folder / "all_results.csv")
significant.write_csv(
    output_folder / "significant_results.csv"
)
top_greater.write_csv(
    output_folder / "top_greater_results.csv"
)

# Make a publication-style overview of the greater results.
EnrichmentPlots.bubble_plot(
    greater,
    top_n=15,
    title="GSE16873: greater-direction KEGG enrichment",
    output_file=output_folder / "greater_bubble.png",
)

# Save a small software and input record beside the results.
record_lines = [
    f"PyGAGE version: {pygage.__version__}",
    f"Python version: {sys.version.split()[0]}",
    f"Operating system: {platform.platform()}",
    f"Prepared input: {prepared_path}",
    f"Gene-set input: {gene_sets_path}",
    f"Prepared shape: {prepared.shape}",
    f"Gene-set count: {len(gene_sets)}",
    "Input state: prepared paired fold-change matrix",
    "Test method: t-test",
    "Meta-method: stouffer",
    "Set-size range: 10 through 500 matched genes",
    "Directions: greater and less",
    "Significant-result rule: q_val below 0.05",
]

(output_folder / "analysis_record.txt").write_text(
    "\n".join(record_lines) + "\n",
    encoding="utf-8",
)

print("Top five greater-direction pathways:")
print(
    greater.select(
        [
            "gene_set",
            "set_size",
            "stat_mean",
            "p_val",
            "q_val",
        ]
    ).head(5)
)

print("Saved output in:", output_folder.resolve())
```

## 2. Run the analysis

Activate the project environment, then run:

```bash
python gse16873_analysis.py
```

The calculation uses the local package files. It does not contact KEGG or
another database.

## 3. Check what was loaded

The first lines include:

```text
Prepared table shape: (11979, 7)
Prepared columns: ['gene_id', 'DCIS_1', 'DCIS_2', 'DCIS_3', 'DCIS_4', 'DCIS_5', 'DCIS_6']
Number of gene sets: 177
```

The shape `(11979, 7)` means:

- 11,979 rows, one for each measured gene; and
- seven columns, consisting of one identifier plus six comparisons.

## 4. Check the leading results

With PyGAGE 1.2.1 and the packaged files, the first three
greater-direction rows are:

| Gene set | Matched set size | Approximate p-value |
| --- | ---: | ---: |
| `hsa04141 Protein processing in endoplasmic reticulum` | 144 | `9.2366e-18` |
| `hsa00190 Oxidative phosphorylation` | 97 | `3.2793e-12` |
| `hsa03050 Proteasome` | 39 | `2.1085e-10` |

These are enrichment results for this prepared comparison. Biological
interpretation should also consider the study design, measured tissue,
preprocessing, matched identifiers, and the gene-set release.

## Understand how the package files are found

This line locates the installed PyGAGE source:

```python
package_folder = Path(core.__file__).resolve().parent
```

`core.__file__` is the installed location of `pygage/core.py`. Its parent is
the package folder. The script then adds:

```text
data/regression
```

This approach works whether PyGAGE was installed from the cloned repository or
from a built 1.2.1 package.

## Understand why gene IDs are read as text

```python
schema_overrides={"gene_id": pl.Utf8}
```

`pl.Utf8` means a text column. Gene identifiers are labels, even when every
character happens to be a number. Reading them as text keeps their exact form
for matching against the gene-set members.

## Understand the JSON step

```python
gene_sets = json.loads(
    gene_sets_path.read_text(encoding="utf-8")
)
```

This happens in two parts:

1. `read_text` reads the JSON file as text.
2. `json.loads` converts that text into a Python dictionary.

The dictionary has this structure:

```text
pathway name -> list of member gene IDs
```

## Understand the analysis call

```python
result = gage(
    prepared,
    gene_sets,
    prepared=True,
)
```

No set-size option is supplied, so PyGAGE uses the standard matched range:

```text
10 through 500 genes
```

The standard analysis also uses:

- t-test gene-set statistics;
- Stouffer cross-column combination;
- separate `greater` and `less` results;
- Benjamini-Hochberg q-values; and
- an `effect` column.

Pages 20 and 21 explain these settings.

## Understand the three result tables

| File | Purpose |
| --- | --- |
| `all_results.csv` | complete tidy output in both directions |
| `significant_results.csv` | rows passing the recorded q-value rule |
| `top_greater_results.csv` | first 20 greater rows sorted by p-value |

Keep `all_results.csv` even when the main report uses a filtered table. It
preserves the complete statistical result.

## Understand the bubble plot

`greater_bubble.png` summarizes 15 leading greater-direction gene sets:

- horizontal position shows `stat_mean`;
- color shows `-log10(q_val)`; and
- point size shows `set_size`.

Page 23 explains every plotting helper.

## Understand the analysis record

`analysis_record.txt` keeps the software version, Python version, platform,
input locations, input sizes, standard settings, and filtering rule beside the
results.

For a research project, also record:

- the source and release date of externally downloaded gene sets;
- the identifier system;
- the preprocessing method;
- the exact reference and sample definitions;
- any settings changed from the defaults; and
- the script or notebook used to produce the files.

## Adapt this workflow to your own prepared data

After practicing with the packaged files, replace only the loading section:

```python
prepared_path = Path("data") / "my_prepared_matrix.csv"
gene_sets_path = Path("data") / "my_gene_sets.json"

prepared = pl.read_csv(
    prepared_path,
    schema_overrides={"gene_id": pl.Utf8},
)
gene_sets = json.loads(
    gene_sets_path.read_text(encoding="utf-8")
)
```

Keep the remaining analysis, filtering, plotting, and recording steps. Confirm
that the gene identifiers in the two files use the same system.

## Real-data checklist

You are finished when:

- the script finds both packaged input files;
- the prepared shape is `(11979, 7)`;
- 177 gene sets are loaded;
- all five output files exist;
- the leading pathway table is printed;
- the bubble plot opens as an image; and
- the analysis record states PyGAGE 1.2.1.

[<- Previous: Use a Jupyter notebook](25-notebooks.md) | [Home](index.md) | [Next: Configure performance and threads ->](27-performance.md)
