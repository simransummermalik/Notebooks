# Download organism-specific KEGG gene sets

*Page 15 of 31*

Use this page when your measurements belong to an organism that has a KEGG
organism code, such as `hsa` for human or `mmu` for mouse.

PyGAGE 1.2.1 can retrieve the pathway names and pathway members from the KEGG
REST service. After one download, you can save the gene sets as JSON and reuse
them in later analyses.

## Understand what PyGAGE downloads

An organism-specific KEGG download connects pathway IDs to gene IDs:

```text
hsa04110 -> 1019, 1021, 1026, ...
hsa04115 -> 7157, 5728, 1111, ...
```

The returned Python dictionary contains three parts:

| Key | Contents |
| --- | --- |
| `gene_sets` | pathway ID to member-gene IDs |
| `pathway_names` | pathway ID to readable pathway name |
| `categories` | pathway IDs grouped into broad KEGG categories |

The category dictionary contains `metabolism`, `genetic_info`, `signaling`,
`disease`, `drug`, and `other`. It also contains the convenience groups
`sigmet`, `sig`, `met`, and `dise`.

## Choose one identifier type

The `id_type` setting controls the identifiers placed inside each gene set:

| Setting | Member IDs | Example |
| --- | --- | --- |
| `"entrez"` | NCBI Entrez Gene IDs | `"7157"` |
| `"kegg"` | native KEGG gene IDs with the organism prefix removed | organism-specific |

Use the same identifier system in both places:

```text
measurement-table IDs == gene-set member IDs
```

For example, use `id_type="entrez"` when the first column of the measurement
table contains Entrez IDs. Store IDs as text even when they contain only
numbers.

## Find an organism code

Common examples include:

| Organism | KEGG code |
| --- | --- |
| human | `hsa` |
| mouse | `mmu` |
| rat | `rno` |
| fruit fly | `dme` |
| budding yeast | `sce` |
| *Escherichia coli* K-12 MG1655 | `eco` |
| *Arabidopsis thaliana* | `ath` |

PyGAGE can retrieve the current organism list:

```python
from pygage.pathway_database_utils import KEGGPathwayRetriever

kegg = KEGGPathwayRetriever(cache_dir="pygage_cache/kegg")
organisms = kegg.list_organisms()

print(organisms["hsa"])
print(organisms["mmu"])
```

`list_organisms()` returns a dictionary whose keys are KEGG organism codes.

## Download a reproducible JSON file

Create a file named `download_kegg_human.py` in your project folder. Paste this
complete script:

```python
import json
from datetime import date
from pathlib import Path

import pygage
from pygage.pathway_database_utils import KEGGPathwayRetriever


species = "hsa"
identifier_type = "entrez"

cache_folder = Path("pygage_cache/kegg")
output_folder = Path("gene_sets")
output_folder.mkdir(exist_ok=True)

kegg = KEGGPathwayRetriever(cache_dir=cache_folder)

# Confirm the organism code and retrieve its pathway membership.
species_record = kegg.get_species_code(species)
download = kegg.get_pathway_genes(
    species=species,
    id_type=identifier_type,
)

# Save the downloaded data together with a small provenance record.
payload = {
    "gene_sets": download["gene_sets"],
    "set_names": download["pathway_names"],
    "categories": download["categories"],
    "provenance": {
        "source": "KEGG REST",
        "species_code": species,
        "species_name": species_record["name"],
        "identifier_type": identifier_type,
        "retrieved": date.today().isoformat(),
        "pygage_version": pygage.__version__,
    },
}

output_file = output_folder / "kegg_hsa_entrez.json"
output_file.write_text(json.dumps(payload, indent=2))

print("Species:", species_record["name"])
print("Pathways downloaded:", len(payload["gene_sets"]))
print("Saved:", output_file)
```

Run it:

```bash
python download_kegg_human.py
```

The script creates:

```text
gene_sets/kegg_hsa_entrez.json
pygage_cache/kegg/
```

The JSON file is the portable gene-set file. The cache folder stores individual
KEGG responses so PyGAGE can reuse them on later runs.

## Understand the internet and cache steps

The first retrieval contacts `https://rest.kegg.jp`. PyGAGE requests:

- the organism record;
- the pathway names;
- the pathway-to-gene links;
- the Entrez conversion table when `id_type="entrez"`; and
- the KEGG pathway hierarchy used for categories.

When `cache_dir` is set, successful text responses are saved locally. A later
request for the same resource reads the matching cache file first.

This gives a simple workflow:

```text
first run: internet -> local cache -> saved JSON
later run: local cache or saved JSON -> analysis
```

Keep the JSON file and its provenance block with the analysis results.

## Open the downloaded file in Python

Use this pattern in an analysis script:

```python
import json
from pathlib import Path

from pygage import gage, read_matrix


payload = json.loads(
    Path("gene_sets/kegg_hsa_entrez.json").read_text()
)
gene_sets = payload["gene_sets"]

expression = read_matrix("expression.csv")

result = gage(
    expression,
    gene_sets,
    ref_indices=[0, 1, 2],
    samp_indices=[3, 4, 5],
)

result.write_csv("kegg_enrichment.csv")
```

The reference and sample indices count only the numeric sample columns. They do
not count the gene-ID column.

## Download from Terminal instead

The equivalent command-line download is:

```bash
python -c "from pathlib import Path; Path('gene_sets').mkdir(exist_ok=True)"

pygage kegg pathway \
  --output gene_sets/kegg_hsa_entrez.json \
  --species hsa \
  --id-type entrez \
  --cache pygage_cache/kegg
```

The command writes `gene_sets`, `set_names`, and `categories` to JSON. Page 24
lists every command-line option.

## Python reference for the KEGG retriever

```python
KEGGPathwayRetriever(
    cache_dir=None,
    retries=3,
    pause=0.34,
)
```

| Part | Default | Meaning |
| --- | --- | --- |
| `cache_dir` | `None` | optional folder for KEGG text responses |
| `retries` | `3` | number of request attempts |
| `pause` | `0.34` | delay between requests in seconds |

Useful methods are:

```python
kegg.list_organisms()
kegg.get_species_code("hsa")
kegg.get_pathway_names("hsa")
kegg.get_pathway_genes("hsa", id_type="entrez")
kegg.get_module_gene_sets("hsa")
```

`get_module_gene_sets()` returns `gene_sets` and `module_names` when KEGG
modules are the desired grouping.

## Final checklist

- the KEGG organism code matches the studied organism;
- `id_type` matches the measurement-table IDs;
- the downloaded JSON file has been saved;
- the provenance block records species, ID type, date, and PyGAGE version;
- the cache folder is kept for reproducible reuse; and
- the expression and gene-set identifiers are stored as text.

[<- Previous: Use pandas or AnnData](14-pandas-anndata.md) | [Home](index.md) | [Next: Use KEGG Orthology ->](16-kegg-orthology.md)
