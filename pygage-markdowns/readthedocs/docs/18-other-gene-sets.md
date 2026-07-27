# Use Reactome, MSigDB, and GMT gene sets

*Page 18 of 31*

Use this page when the gene sets come from Reactome, MSigDB, or another
resource that supplies a GMT file.

These PyGAGE 1.2.1 loaders read local files. You select and download the
desired release first, then PyGAGE parses it into a provenance-aware
`GeneSetCollection`.

## Understand a GMT file

GMT means Gene Matrix Transposed. Each line represents one gene set:

```text
set name<TAB>description<TAB>gene 1<TAB>gene 2<TAB>gene 3
```

A tiny example is:

```text
Cell cycle	curated example	1019	1021	1026
DNA repair	curated example	672	675	7157
```

The separators must be tab characters, not commas or spaces.

PyGAGE reads:

- an uncompressed `.gmt` file; or
- a gzip-compressed GMT file whose final suffix is `.gz`.

The result is a dictionary of set names and members stored inside a
`GeneSetCollection`.

## Load any GMT file

```python
from pygage.gene_sets import load_gmt


collection = load_gmt(
    "reference_files/pathways.gmt",
    source="My pathway resource",
    release="2026-07",
)

print("Sets:", collection.n_sets)
print(collection.metadata())
```

The exact signature is:

```python
load_gmt(
    path,
    source="GMT",
    release="unknown",
)
```

Set `source` and `release` to the labels supplied with the downloaded file.
The local filename is stored in `collection.extra["file"]`.

## MSigDB

MSigDB distributes collections such as Hallmark, C2, and C5 in GMT format.
Choose a file whose identifier type and species match the measurement table.

### Option A: use the MSigDB convenience loader

```python
from pygage.gene_sets import load_msigdb


hallmark = load_msigdb(
    "reference_files/hallmark_symbols.gmt",
    collection="H",
)

hallmark.release = "replace-with-MSigDB-release"

print(hallmark.metadata())
```

The exact signature is:

```python
load_msigdb(
    path,
    collection="H",
)
```

The collection code is stored in `extra["collection"]`.

### Option B: record the release in the loader call

Because MSigDB files are valid GMT, `load_gmt()` can attach both source and
release immediately:

```python
from pygage.gene_sets import load_gmt


hallmark = load_gmt(
    "reference_files/hallmark_symbols.gmt",
    source="MSigDB Hallmark",
    release="replace-with-MSigDB-release",
)
```

Both options produce gene sets that PyGAGE can analyze.

## Reactome

PyGAGE supports two local Reactome layouts.

### Reactome GMT

```python
from pygage.gene_sets import load_reactome


reactome = load_reactome(
    "reference_files/ReactomePathways.gmt",
    id_type="gmt",
    species="Homo sapiens",
)

reactome.release = "replace-with-Reactome-release"
print(reactome.metadata())
```

The GMT file already provides pathway-to-gene membership. The `species` label
is recorded in the collection metadata.

### NCBI2Reactome mapping

The NCBI2Reactome all-levels mapping contains six tab-separated fields:

```text
gene ID
pathway ID
URL
pathway name
evidence
species
```

Load and filter it by the exact species name:

```python
from pygage.gene_sets import load_reactome


reactome = load_reactome(
    "reference_files/NCBI2Reactome_All_Levels.txt",
    id_type="ncbi2reactome",
    species="Homo sapiens",
)

reactome.release = "replace-with-Reactome-release"
print("Reactome pathways:", reactome.n_sets)
```

The exact signature is:

```python
load_reactome(
    path,
    id_type="gmt",
    species="Homo sapiens",
)
```

For `ncbi2reactome`, rows are grouped by pathway ID and duplicate genes are
removed.

## Match the identifier system

The filename or resource documentation may identify a GMT as:

- gene symbols;
- Entrez Gene IDs;
- Ensembl IDs; or
- another identifier system.

Choose a file matching the measurement table.

For example:

```text
measurement table: Entrez IDs
gene-set file:     Entrez IDs
```

These do not match:

```text
measurement table: TP53
gene-set file:     7157
```

Page 9 explains exact identifier matching. If conversion is required,
`GeneIDConverter` converts between the packaged Entrez and symbol mapping:

```python
from pygage.gene_id_utils import GeneIDConverter


converter = GeneIDConverter()
entrez_ids = converter.sym2eg(["TP53", "BRCA1"])

print(entrez_ids)
```

Do not infer an identifier type from the fact that a value looks numeric;
record the source description.

## Save a collection in the PyGAGE cache

All three loader routes can use the same cache class:

```python
from pygage.gene_sets import GeneSetCache


cache = GeneSetCache(
    cache_dir="pygage_cache/gene_sets"
)

saved_path = cache.save(
    "reactome_human_release",
    reactome,
)

print("Saved:", saved_path)
print("Available keys:", cache.list_keys())
```

Load it later:

```python
from pygage.gene_sets import GeneSetCache


cache = GeneSetCache("pygage_cache/gene_sets")
reactome = cache.load("reactome_human_release")

print(reactome.metadata())
```

The cache file contains both `gene_sets` and `metadata` in gzip-compressed
JSON. The collection metadata records source, release, retrieval date, set
count, a short checksum, and extra source details.

## Export a portable JSON file

The command-line `run` subcommand accepts a plain JSON mapping or a JSON object
with a top-level `gene_sets` key. Create the second form:

```python
import json
from pathlib import Path


Path("gene_sets").mkdir(exist_ok=True)

payload = {
    "gene_sets": reactome.as_dict(),
    "metadata": reactome.metadata(),
}

Path("gene_sets/reactome_human.json").write_text(
    json.dumps(payload, indent=2)
)
```

It can then be used from Terminal:

```bash
pygage run expression.csv \
  --gene-sets gene_sets/reactome_human.json \
  --output reactome_results.csv \
  --ref 0,1,2 \
  --samp 3,4,5
```

## Run directly from Python

```python
from pygage import gage, read_matrix
from pygage.gene_sets import load_gmt


expression = read_matrix("expression.csv")

gene_sets = load_gmt(
    "reference_files/pathways.gmt",
    source="My pathway resource",
    release="2026-07",
)

result = gage(
    expression,
    gene_sets,
    ref_indices=[0, 1, 2],
    samp_indices=[3, 4, 5],
)

result.write_csv("gmt_enrichment_results.csv")
```

## Local files, network, and reproducibility

`load_gmt()`, `load_msigdb()`, and `load_reactome()` do not contact an online
service. They parse the file path supplied to them.

This creates a clear provenance chain:

```text
chosen database release
        |
        v
saved source file
        |
        v
PyGAGE GeneSetCollection
        |
        v
cached collection and enrichment result
```

Keep:

- the original downloaded file;
- its database name and release;
- its species and identifier type;
- the collection metadata;
- the analysis command or script; and
- the PyGAGE result file.

## Final checklist

- the file is valid tab-separated GMT or a supported Reactome mapping;
- compressed direct-loader files end in `.gz`;
- source, release, species, and identifier type are recorded;
- measurement IDs and member IDs match;
- the collection metadata has been reviewed;
- an offline cache or portable JSON copy was saved; and
- the result was written to a new filename.

[<- Previous: Build Gene Ontology sets](17-gene-ontology.md) | [Home](index.md) | [Next: Understand every result column ->](19-results.md)
