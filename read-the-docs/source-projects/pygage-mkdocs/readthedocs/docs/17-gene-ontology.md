# Build Gene Ontology gene sets

*Page 17 of 31*

Use this page when you want to test Gene Ontology, or GO, terms.

PyGAGE 1.2.1 builds GO gene sets from local annotation files. This keeps the
exact annotation source under your control and makes it easy to save a dated,
reusable collection.

## Understand the two GO files

The workflow can use two files:

| File | Required? | Purpose |
| --- | --- | --- |
| GAF annotation file | yes | connects genes to GO term IDs |
| OBO ontology file | optional | supplies GO names and parent relationships |

A GAF is a tab-separated Gene Association Format file. Use a GAF matching the
studied organism and identifier system.

The commonly used ontology file is named `go-basic.obo`. It allows PyGAGE to
propagate an annotation from a child term to its `is_a` and `part_of`
ancestors.

For the clearest beginner workflow, place uncompressed files in:

```text
reference_files/
├── annotations.gaf
└── go-basic.obo
```

These files are supplied locally to PyGAGE. Download them from the Gene
Ontology resource or the appropriate organism annotation database before
running the loader.

## Choose a GO domain

GO has three domains:

| Setting | Full name | Describes |
| --- | --- | --- |
| `"BP"` | Biological Process | larger biological programs |
| `"MF"` | Molecular Function | activities performed by gene products |
| `"CC"` | Cellular Component | cellular locations or structures |
| `None` | all domains | BP, MF, and CC together |

Beginning with one domain makes the first result easier to review.

## Choose the GAF identifier column

The `id_field` argument has two choices:

| Setting | GAF value used |
| --- | --- |
| `"symbol"` | gene symbol from GAF column 3 |
| `"object_id"` | database object ID from GAF column 2 |

Choose the field that matches the first column of the measurement table.

For example:

```text
measurement IDs = TP53, BRCA1, EGFR
GO id_field      = symbol
```

Identifier matching is exact. Store the IDs as text and review capitalization.

## Decide how to treat annotations

Two settings control GO membership:

### Electronic annotations

```python
include_iea=True
```

The default keeps annotations whose evidence code is `IEA`, meaning inferred
from electronic annotation.

Use:

```python
include_iea=False
```

when the analysis plan excludes IEA evidence.

### Parent propagation

```python
propagate=True
```

With an OBO file, this adds a gene to the ancestors of its directly annotated
term through `is_a` and `part_of` relationships.

Use:

```python
propagate=False
```

to keep only direct GAF annotations. This is the default.

Rows marked with the GAF qualifier `NOT` are excluded automatically.

## Build and cache a GO collection

Create `build_go_gene_sets.py`:

```python
from pathlib import Path

from pygage.gene_sets import GeneSetCache, load_go


gaf_file = Path("reference_files/annotations.gaf")
obo_file = Path("reference_files/go-basic.obo")

go_collection = load_go(
    gaf_path=gaf_file,
    obo_path=str(obo_file),
    aspect="BP",
    id_field="symbol",
    include_iea=True,
    propagate=True,
)

# Replace this text with the release date recorded for your downloaded files.
go_collection.release = "replace-with-GO-release-date"
go_collection.extra["gaf_file"] = str(gaf_file)
go_collection.extra["obo_file"] = str(obo_file)

cache = GeneSetCache(
    cache_dir="pygage_cache/gene_sets"
)
cache_file = cache.save(
    "go_bp_with_iea_propagated",
    go_collection,
)

print("GO sets:", go_collection.n_sets)
print("Checksum:", go_collection.checksum)
print("Metadata:", go_collection.metadata())
print("Saved cache:", cache_file)
```

Run it:

```bash
python build_go_gene_sets.py
```

The cache file is compressed JSON:

```text
pygage_cache/gene_sets/go_bp_with_iea_propagated.json.gz
```

## Understand the provenance metadata

Every `GeneSetCollection` records:

| Field | Meaning |
| --- | --- |
| `source` | loader source, here `GO` |
| `release` | release label supplied for the collection |
| `retrieved` | date the collection object was created |
| `n_sets` | number of GO terms |
| `checksum` | short content checksum |
| `extra` | aspect, propagation, file labels, and related details |

`load_go()` records the chosen aspect, whether propagation was used, and
whether an OBO file was supplied. The script adds the filenames and release
label so another researcher can identify the inputs.

## Load the cached collection later

```python
from pygage.gene_sets import GeneSetCache


cache = GeneSetCache(
    cache_dir="pygage_cache/gene_sets"
)

go_collection = cache.load(
    "go_bp_with_iea_propagated"
)

print(go_collection.metadata())
```

The cache stores the gene sets and their metadata together. The checksum is
recomputed when the collection is reconstructed.

## Run enrichment with the GO sets

```python
from pygage import gage, read_matrix
from pygage.gene_sets import GeneSetCache


expression = read_matrix("expression.csv")

cache = GeneSetCache("pygage_cache/gene_sets")
go_collection = cache.load("go_bp_with_iea_propagated")

result = gage(
    expression,
    go_collection,
    ref_indices=[0, 1, 2],
    samp_indices=[3, 4, 5],
)

result.write_csv("go_bp_enrichment.csv")
```

PyGAGE accepts the complete `GeneSetCollection`; calling
`go_collection.as_dict()` is optional.

## Use the command line

This command builds BP sets, keeps IEA annotations, and propagates to parent
terms:

```bash
python -c "from pathlib import Path; Path('gene_sets').mkdir(exist_ok=True)"

pygage go reference_files/annotations.gaf \
  --output gene_sets/go_bp.json \
  --obo reference_files/go-basic.obo \
  --aspect BP \
  --id-field symbol \
  --propagate
```

Add `--no-iea` when IEA annotations should be excluded:

```bash
pygage go reference_files/annotations.gaf \
  --output gene_sets/go_bp_without_iea.json \
  --obo reference_files/go-basic.obo \
  --aspect BP \
  --id-field symbol \
  --no-iea \
  --propagate
```

The command writes a JSON object containing `gene_sets` and `metadata`.

## Look up GO term names

The low-level retriever returns term names when an OBO file is supplied:

```python
from pathlib import Path

from pygage.pathway_database_utils import GOGeneSetRetriever


retriever = GOGeneSetRetriever()
go_data = retriever.get_go_gene_sets(
    annotation_file=Path("reference_files/annotations.gaf"),
    id_field="symbol",
    include_iea=True,
    obo_file=Path("reference_files/go-basic.obo"),
)

print(go_data["go_names"].get("GO:0008150"))
```

The returned dictionary contains:

- `gene_sets`;
- `go_categories`; and
- `go_names`.

Use `load_go()` for the convenient provenance-aware collection and
`GOGeneSetRetriever` when the separate name dictionary is needed.

## Exact Python signature

```python
load_go(
    gaf_path,
    obo_path=None,
    aspect=None,
    id_field="symbol",
    include_iea=True,
    propagate=False,
)
```

## Final checklist

- the GAF matches the organism;
- `id_field` matches the measurement identifiers;
- BP, MF, CC, or all domains was selected intentionally;
- the IEA choice was recorded;
- the propagation choice and OBO file were recorded;
- the source release or download date was added to metadata;
- the cached collection was saved; and
- the result table was written to a separate output file.

[<- Previous: Use KEGG Orthology](16-kegg-orthology.md) | [Home](index.md) | [Next: Use other gene-set sources ->](18-other-gene-sets.md)
