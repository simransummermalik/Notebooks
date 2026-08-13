# Work with KEGG files and pathway tables

*Page 19 of 24*

Use this page when you want to understand the KEGG files that Pathview Plus
retrieves, reuse a local pathway file, inspect pathway nodes, or connect an
enrichment result to a pathway batch.

## What Pathview Plus does automatically

The main `pathview()` function completes a short KEGG workflow for you:

```text
species + pathway number
          |
          v
check kegg_dir for pathway files
          |
          v
retrieve any required files that are not already there
          |
          v
read KGML nodes, edges, reactions, and coordinates
          |
          v
match data, assign colors, and write the finished image
```

For this call:

```python
from pathlib import Path

from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

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
    out_suffix="pi3k_akt",
)
```

Pathview Plus combines `hsa` and `04151` into the full pathway ID
`hsa04151`. The folder can then contain:

```text
pathview_output/
├── hsa04151.xml
├── hsa04151.png
└── hsa04151.pi3k_akt.png
```

The files have different jobs:

| File | Purpose |
| --- | --- |
| `hsa04151.xml` | KEGG Markup Language, or KGML, describing pathway entries, connections, reactions, and drawing coordinates |
| `hsa04151.png` | the KEGG native pathway picture used as the background |
| `hsa04151.pi3k_akt.png` | the finished image containing the mapped colors |

`kegg_dir` is both the pathway-file folder and the output folder. When a
required KEGG file with the expected name is already there, Pathview Plus
reuses it. This makes one project folder a consistent cache for repeated runs.

For native PNG output, the workflow uses the XML and KEGG PNG. SVG and PDF
workflows with `kegg_native=False` use the XML pathway structure. Page 15 explains all
[output-format combinations](15-output-formats.md).

## Download KEGG files directly

Use `download_kegg()` when you want to prepare the source files before the
mapping step.

```python
from pathlib import Path

from pathview import download_kegg


kegg_folder = Path("pathview_output")

status = download_kegg(
    pathway_id="04151",
    species="hsa",
    kegg_dir=kegg_folder,
    file_type=["xml", "png"],
)

print(status)
```

The numeric pathway ID is combined with the species code. The files are saved
as:

```text
pathview_output/hsa04151.xml
pathview_output/hsa04151.png
```

Choose which source files to request with `file_type`:

```python
download_kegg(
    "04151",
    species="hsa",
    kegg_dir="pathview_output",
    file_type=["xml"],
)
```

Use `["xml"]` for KGML only, `["png"]` for the native picture only, or omit
`file_type` to request both. The returned dictionary uses the full pathway ID
as its key, so printing it records the result of the retrieval step.

## Resolve a KEGG species

`kegg_species_code()` looks up a species in the KEGG organism information and
returns a `SpeciesInfo` object.

```python
from pathview import kegg_species_code


human = kegg_species_code("hsa")

print(human.kegg_code)
print(human.entrez_gnodes)
```

For an organism-specific workflow, `kegg_code` is the short code used in
pathway filenames and API requests. `kegg_species_code("ko")` returns the KEGG
Orthology reference information used for KO pathways.

Every `SpeciesInfo` object has these fields:

| Field | Meaning |
| --- | --- |
| `kegg_code` | KEGG organism code, or `ko` |
| `entrez_gnodes` | whether gene nodes are treated as Entrez-based organism genes |
| `kegg_geneid` | stored KEGG gene or orthology identifier metadata |
| `ncbi_geneid` | stored NCBI Gene identifier metadata |
| `ncbi_proteinid` | stored NCBI Protein identifier metadata |
| `uniprot` | stored UniProt identifier metadata |

The first five pages show the simplest way to select and use a
[pathway and species](05-choose-a-pathway.md).

## Inspect a KGML file

KGML is an XML description of a KEGG pathway. `parse_kgml()` turns that file
into Python objects. `node_info()` then turns its nodes into a Polars table.

```python
from pathview import node_info, parse_kgml


pathway = parse_kgml("pathview_output/hsa04151.xml")

print(pathway.pathway_id)
print(pathway.pathway_name)
print(len(pathway.nodes))
print(len(pathway.edges))
print(len(pathway.reactions))

nodes = node_info(pathway)
print(nodes.head())
```

The node table has one row for each parsed pathway entry and these columns:

| Column | Meaning |
| --- | --- |
| `entry_id` | internal entry identifier within the KGML pathway |
| `name` | KEGG identifier or identifiers attached to the entry |
| `type` | entry type, such as gene, ortholog, compound, map, or group |
| `x`, `y` | center coordinates on the pathway |
| `width`, `height` | dimensions of the pathway shape |
| `bgcolor` | background color stored in KGML |
| `label` | text stored for the shape |
| `shape` | shape type |
| `reaction` | associated reaction name or names |
| `component` | component entry IDs for a grouped entry |
| `size` | number used to describe the entry or group size |

This table is useful for reviewing pathway contents or building an advanced
rendering workflow.

## Inspect the tables returned by `pathview()`

The main function returns a dictionary with two keys:

```python
gene_nodes = result.get("plot_data_gene")
compound_nodes = result.get("plot_data_cpd")
```

| Key | Contents |
| --- | --- |
| `plot_data_gene` | mapped gene nodes, or mapped ortholog nodes for a KO pathway |
| `plot_data_cpd` | mapped compound nodes |

Each available table is a Polars DataFrame. It carries pathway metadata such
as the entry ID, name, type, coordinates, dimensions, label, and shape,
together with the numeric columns supplied in the input data.

You can inspect or save a table:

```python
if gene_nodes is not None:
    print(gene_nodes.head())
    gene_nodes.write_csv(
        "pathview_output/hsa04151.mapped_gene_nodes.tsv",
        separator="\t",
    )
```

The saved table provides a record of the pathway entries connected to the
analysis values.

## Connect enrichment results to a pathway batch

A pathway-enrichment table helps choose which pathways to draw. A molecular
results table supplies the gene-level values that become colors.

Keep those two roles separate:

```text
enrichment result -> selects pathway IDs
gene result table -> supplies one value per gene
```

For example, an enrichment file may begin like this:

| pathway_id | adjusted_p_value |
| --- | ---: |
| hsa04151 | 0.002 |
| hsa04010 | 0.008 |
| hsa04110 | 0.021 |

This example selects up to ten pathways and maps the same gene-level result
table onto each one:

```python
from pathlib import Path

import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

enrichment = pl.read_csv(
    "pathway_enrichment.tsv",
    separator="\t",
)

gene_data = (
    pl.read_csv("gene_results.tsv", separator="\t")
    .select(["entrez_id", "log2_fold_change"])
    .with_columns(pl.col("entrez_id").cast(pl.String))
)

selected_ids = (
    enrichment
    .filter(pl.col("adjusted_p_value") <= 0.05)
    .sort("adjusted_p_value")
    .head(10)
    .with_columns(
        pl.col("pathway_id")
        .cast(pl.String)
        .str.extract(r"(\d{5})$", 1)
        .alias("kegg_number")
    )
    .drop_nulls("kegg_number")
    .get_column("kegg_number")
    .unique(maintain_order=True)
    .to_list()
)

output_folder = Path("pathview_output")
output_folder.mkdir(exist_ok=True)

for pathway_id in selected_ids:
    pathview(
        pathway_id=pathway_id,
        species="hsa",
        gene_data=gene_data,
        gene_idtype="ENTREZ",
        map_symbol=False,
        kegg_dir=output_folder,
        kegg_native=True,
        output_format="png",
        out_suffix=f"enrichment_{pathway_id}",
    )
```

The adjusted p-value is used to select and order pathways. The
`log2_fold_change` values are used to color the genes. Page 11 explains the
basic [many-pathways loop](11-many-pathways.md).

## Complete KEGG and KGML reference

These are the public Pathview Plus 2.0.2 KEGG and KGML tools:

| Public name | Call or fields | Result |
| --- | --- | --- |
| `kegg_species_code` | `kegg_species_code(species="hsa")` | a `SpeciesInfo` object |
| `SpeciesInfo` | `kegg_code`, `entrez_gnodes`, `kegg_geneid`, `ncbi_geneid`, `ncbi_proteinid`, `uniprot` | species metadata |
| `download_kegg` | `download_kegg(pathway_id, species="hsa", kegg_dir=Path("."), file_type=None)` | retrieval-status dictionary and saved XML or PNG files |
| `parse_kgml` | `parse_kgml(filepath)` | a `KGMLPathway` object |
| `node_info` | `node_info(pathway)` | a Polars node DataFrame |
| `KGMLPathway` | `pathway_id`, `pathway_name`, `nodes`, `edges`, `reactions` | complete parsed pathway container |
| `KGMLNode` | `entry_id`, `name`, `node_type`, `link`, `reaction`, `x`, `y`, `width`, `height`, `bgcolor`, `label`, `shape`, `component` | one KGML entry |
| `KGMLEdge` | `entry1`, `entry2`, `edge_type`, `subtypes` | one KGML relation |
| `KGMLReaction` | `name`, `rxn_type`, `substrates`, `products` | one KGML reaction |

All of these names can be imported from `pathview`:

```python
from pathview import (
    KGMLEdge,
    KGMLNode,
    KGMLPathway,
    KGMLReaction,
    SpeciesInfo,
    download_kegg,
    kegg_species_code,
    node_info,
    parse_kgml,
)
```

Use `pathview()` for the complete data-to-image workflow. Use the individual
KEGG and KGML tools when you want to prepare files, inspect pathway structure,
or build a more specialized workflow.

[<- Previous: Use the command line](18-command-line.md) | [Home](index.md) | [Next: Work with SBGN and pathway databases ->](20-sbgn-and-databases.md)
