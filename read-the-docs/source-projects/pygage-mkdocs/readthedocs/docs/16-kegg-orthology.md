# Use KEGG Orthology gene sets

*Page 16 of 31*

Use this page when the measured features have KEGG Orthology identifiers, also
called KO IDs.

A KO ID describes a functional ortholog group:

```text
K00844
K02586
K12407
```

KO gene sets are species-independent. They are useful for genomes,
metagenomes, viromes, phages, microbial communities, and organisms that do not
have a dedicated KEGG genome entry.

## Understand the KO workflow

The complete workflow is:

```text
genes or proteins
        |
        v
functional annotation assigns KO IDs
        |
        v
measurements are summarized by KO
        |
        v
PyGAGE tests KO pathways or KO modules
```

PyGAGE 1.2.1 starts with the KO-level table. Functional annotation is performed
before the enrichment analysis.

## Download KO pathway gene sets

The simplest method is the PyGAGE command line:

```bash
python -c "from pathlib import Path; Path('gene_sets').mkdir(exist_ok=True)"

pygage kegg ko \
  --output gene_sets/ko_pathways.json \
  --reference pathway \
  --cache pygage_cache/kegg
```

This first download uses the KEGG REST service. PyGAGE saves reusable response
files in `pygage_cache/kegg` and writes the complete portable download to:

```text
gene_sets/ko_pathways.json
```

The JSON file contains:

| Key | Contents |
| --- | --- |
| `gene_sets` | reference pathway or module to KO members |
| `set_names` | readable names for the sets |
| `categories` | broad KEGG categories for pathway sets |
| `ko_catalog` | KO ID to KO description |
| `provenance` | source, reference type, counts, and retrieval date |

The provenance record includes:

- `source`;
- `reference`;
- `n_sets`;
- `n_kos_in_sets`;
- `n_kos_total`;
- `retrieved`; and
- a KEGG use-and-citation note.

Keep this record with the results.

## Choose pathways or modules

`--reference` has two choices:

| Choice | Meaning |
| --- | --- |
| `pathway` | KO members grouped by KEGG reference pathway |
| `module` | KO members grouped by KEGG module |

To download modules:

```bash
pygage kegg ko \
  --output gene_sets/ko_modules.json \
  --reference module \
  --cache pygage_cache/kegg
```

## Download from Python

The same operation is available in a Python script:

```python
from pathlib import Path

from pygage.pathway_database_utils import KEGGPathwayRetriever


output_folder = Path("gene_sets")
output_folder.mkdir(exist_ok=True)

kegg = KEGGPathwayRetriever(
    cache_dir=Path("pygage_cache/kegg")
)

payload = kegg.download_ko_gene_sets(
    output_file=output_folder / "ko_pathways.json",
    reference="pathway",
)

print("Gene sets:", payload["provenance"]["n_sets"])
print("KO IDs in sets:", payload["provenance"]["n_kos_in_sets"])
print("Saved retrieval date:", payload["provenance"]["retrieved"])
```

Other KO methods are:

```python
ko_sets = kegg.get_ko_gene_sets(reference="pathway")
ko_catalog = kegg.list_all_kos()
```

`get_ko_gene_sets()` returns `gene_sets`, `pathway_names`, and `categories`.
`list_all_kos()` returns a dictionary connecting each KO ID to its description.

## Prepare KO data from MetaCerberus

MetaCerberus can be used before PyGAGE to assign functional annotations. The
exact MetaCerberus output columns depend on the chosen workflow, so first
identify:

- the column containing the original feature, gene, or protein ID; and
- the column containing a KO ID.

For this teaching example, assume a tab-separated annotation file named
`metacerberus_ko.tsv` contains:

```text
feature_id	ko_id
protein_001	K00844
protein_002	K00844
protein_003	K02586
```

Also assume `feature_changes.csv` contains:

```text
feature_id,condition_change
protein_001,1.7
protein_002,2.1
protein_003,-1.4
```

Create `prepare_ko_data.py`:

```python
import polars as pl


# Change these column names if your files use different headers.
annotations = pl.read_csv(
    "metacerberus_ko.tsv",
    separator="\t",
    schema_overrides={"feature_id": pl.Utf8, "ko_id": pl.Utf8},
)

changes = pl.read_csv(
    "feature_changes.csv",
    schema_overrides={"feature_id": pl.Utf8},
)

# Join each measured feature to its KO annotation.
feature_to_ko = changes.join(
    annotations.select(["feature_id", "ko_id"]),
    on="feature_id",
    how="inner",
)

# Several features may share one KO. Average their changes into one KO row.
ko_changes = (
    feature_to_ko
    .drop_nulls(["ko_id", "condition_change"])
    .group_by("ko_id")
    .agg(
        pl.col("condition_change")
        .mean()
        .alias("condition_change")
    )
    .rename({"ko_id": "gene_id"})
    .sort("gene_id")
)

ko_changes.write_csv("ko_changes.csv")

print(ko_changes)
print("Saved: ko_changes.csv")
```

Run it:

```bash
python prepare_ko_data.py
```

This is a preparation pattern, not a required MetaCerberus file layout. Match
the two column names to the actual annotation and measurement files. Decide
and record the aggregation method before combining multiple features into one
KO. This example uses the mean.

## Check the prepared KO table

The result must have one text ID column and one or more numeric value columns:

```text
gene_id,condition_change
K00844,1.9
K02586,-1.4
```

Confirm that:

- every `gene_id` begins with an uppercase `K`;
- the ID contains five digits after `K`;
- blank KO annotations have been removed;
- repeated KOs have been summarized using a recorded method; and
- the numeric column represents a documented comparison or score.

## Run KO enrichment

Create `run_ko_enrichment.py`:

```python
import json
from pathlib import Path

from pygage import gage, read_matrix


ko_data = read_matrix("ko_changes.csv")

download = json.loads(
    Path("gene_sets/ko_pathways.json").read_text()
)
ko_gene_sets = download["gene_sets"]

result = gage(
    ko_data,
    ko_gene_sets,
    prepared=True,
)

result.write_csv("ko_enrichment_results.csv")

print(result.head(10))
print("Saved: ko_enrichment_results.csv")
```

Run:

```bash
python run_ko_enrichment.py
```

The standard set-size range is 10 through 500 matched KOs. PyGAGE counts only
set members that are present in `ko_changes.csv`.

## Why identifier matching matters

KO pathway sets contain IDs such as `K00844`. The measurement table must use
the same KO strings.

These are different identifiers:

```text
K00844       <- KO identifier
hsa:3098     <- organism-specific KEGG gene identifier
3098         <- Entrez Gene identifier
```

Do not combine those systems in one enrichment call. The annotation stage
creates the KO-level bridge.

## Reuse the downloaded file offline

After `ko_pathways.json` has been saved, later analysis scripts only need the
local JSON file:

```python
import json
from pathlib import Path

saved = json.loads(
    Path("gene_sets/ko_pathways.json").read_text()
)

gene_sets = saved["gene_sets"]
provenance = saved["provenance"]
```

The KEGG response cache is also reusable. Keep both the final JSON and the
cache when documenting exactly which reference data were used.

## Final checklist

- functional annotation was completed before PyGAGE;
- the prepared table contains KO IDs rather than feature IDs;
- multiple features per KO were summarized by a recorded rule;
- pathway or module reference was chosen deliberately;
- the JSON provenance block was retained;
- KO IDs match between the table and downloaded sets; and
- the result was saved to a new file.

[<- Previous: Download KEGG gene sets](15-kegg.md) | [Home](index.md) | [Next: Build Gene Ontology sets ->](17-gene-ontology.md)
