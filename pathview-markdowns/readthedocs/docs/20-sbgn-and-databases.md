# Work with SBGN and other pathway databases

*Page 20 of 24*

Use this page when you want to inspect pathway files from Reactome, MetaCyc,
PANTHER, or SMPDB.

These functions are **advanced building blocks**. The beginner workflow on
pages 1–19 uses the high-level `pathview()` function to download, map, and
render KEGG pathways in one workflow. The functions on this page let you build
a separate, custom workflow around SBGN-ML files.

## What SBGN and SBGN-ML mean

**SBGN** stands for Systems Biology Graphical Notation. It is a standard visual
language for showing biological entities, processes, and relationships.

**SBGN-ML** is the XML file format used to store an SBGN diagram. An SBGN-ML
file can describe:

- glyphs, which are diagram objects such as genes, chemicals, processes, and
  compartments;
- arcs, which connect glyphs;
- labels and positions; and
- curve points used to draw connections.

Pathview Plus 2.0.2 can read a local `.sbgn` or SBGN-ML `.xml` file into Python
objects and convert its glyphs to a Polars DataFrame.

## Recognize pathway database IDs

The database functions use these identifier patterns:

| Database | Example ID | Main pathway focus |
| --- | --- | --- |
| Reactome | `R-HSA-109582` | curated biological events and pathways |
| MetaCyc | `PWY-7210` | metabolic pathways |
| PANTHER | `P00001` | protein and signaling pathways |
| SMPDB | `SMP0000001` | small-molecule pathways |

These examples show the pattern of each identifier. Always choose the pathway
ID that matches your own biological question.

## 1. Detect the database from an ID

Create a file named `identify_database.py`:

```python
from pathview import detect_database


pathway_ids = [
    "R-HSA-109582",
    "PWY-7210",
    "P00001",
    "SMP0000001",
]

for pathway_id in pathway_ids:
    database = detect_database(pathway_id)
    print(pathway_id, "->", database)
```

Run it:

```bash
python identify_database.py
```

The result is:

```text
R-HSA-109582 -> reactome
PWY-7210 -> metacyc
P00001 -> panther
SMP0000001 -> smpdb
```

`detect_database()` returns the lowercase database name. An identifier outside
these four patterns returns `None`; KEGG IDs continue through the KEGG workflow
described on [page 19](19-kegg-tools.md).

## 2. Inspect the database catalog

`DATABASE_INFO` is a dictionary with one record for each supported database.

```python
from pathview import DATABASE_INFO


for key, record in DATABASE_INFO.items():
    print(
        key,
        record["name"],
        record["id_pattern"],
        record["example"],
        record["url"],
    )
```

Each record contains:

| Key | Meaning |
| --- | --- |
| `name` | display name of the database |
| `description` | short description |
| `url` | database website |
| `id_pattern` | expected pathway-ID pattern |
| `example` | example pathway ID |
| `downloader` | Pathview Plus downloader function for that database |

This catalog is useful when a script needs to select a database tool after
calling `detect_database()`.

## 3. List Reactome pathways

`list_reactome_pathways()` returns a list of dictionaries. Each dictionary has
the keys `id`, `name`, and `species`.

```python
from pathview import list_reactome_pathways


pathways = list_reactome_pathways(species="Homo sapiens")

for pathway in pathways[:5]:
    print(pathway["id"], pathway["name"], pathway["species"])
```

Use the returned IDs to review possible Reactome pathways before selecting one
for a custom workflow.

## 4. Obtain an SBGN-ML file

The public downloader functions in Pathview Plus 2.0.2 are:

| Function | Signature | Role in a custom workflow |
| --- | --- | --- |
| `download_reactome` | `download_reactome(pathway_id, output_dir=Path("."), species="Homo sapiens")` | requests a Reactome SBGN-ML file |
| `download_metacyc` | `download_metacyc(pathway_id, output_dir=Path("."))` | requests a MetaCyc SBGN export |
| `download_panther` | `download_panther(pathway_id, output_dir=Path("."))` | directs the workflow to a locally obtained PANTHER pathway file |
| `download_smpdb` | `download_smpdb(pathway_id, output_dir=Path("."))` | directs the workflow to a locally obtained SMPDB pathway file |

The functions return a `Path` when a file is saved and `None` when the workflow
continues with a pathway file obtained directly from the provider.

Here is the Reactome pattern:

```python
from pathlib import Path

from pathview import download_reactome


pathway_folder = Path("pathway_files")
pathway_file = download_reactome(
    "R-HSA-109582",
    output_dir=pathway_folder,
)

if pathway_file is not None:
    print("Saved:", pathway_file)
```

Use the same staged approach for every database:

1. confirm the pathway ID on the database website;
2. obtain the pathway's SBGN-ML file;
3. keep the file inside a named project folder; and
4. parse that local file with the next example.

The provider websites are
[Reactome](https://reactome.org/),
[MetaCyc](https://metacyc.org/),
[PANTHER](https://www.pantherdb.org/), and
[SMPDB](https://smpdb.ca/).

## 5. Parse a local SBGN-ML file

Place an SBGN-ML file in `pathway_files`. Replace the example filename below
with the exact name of your file.

```python
from pathlib import Path

from pathview import parse_sbgn, sbgn_to_df


pathway_file = Path("pathway_files") / "R-HSA-109582.sbgn"

# Read the XML file into structured pathway objects.
pathway = parse_sbgn(pathway_file)

print("Pathway ID:", pathway.pathway_id)
print("Diagram language:", pathway.pathway_name)
print("Glyphs:", len(pathway.glyphs))
print("Arcs:", len(pathway.arcs))
print("Compartments:", len(pathway.compartments))

# Convert the glyphs to a Polars table.
node_table = sbgn_to_df(pathway)

print(
    node_table.select(
        ["entry_id", "label", "type", "x", "y", "shape"]
    ).head()
)
```

`parse_sbgn()` returns an `SBGNPathway`. `sbgn_to_df()` converts the pathway's
non-compartment glyphs to a Polars DataFrame.

## Understand the parsed Python objects

### `SBGNPathway`

| Attribute | Contents |
| --- | --- |
| `pathway_id` | ID stored on the SBGN map, or the input filename |
| `pathway_name` | SBGN map language stored in the file |
| `glyphs` | dictionary of glyph ID to `SBGNGlyph` |
| `arcs` | list of `SBGNArc` objects |
| `compartments` | dictionary of compartment glyphs |

### `SBGNGlyph`

Each glyph stores:

- `glyph_id` and `glyph_class`;
- `label`;
- center position `x` and `y`;
- `width` and `height`;
- a compartment reference;
- clone-marker information;
- state variables; and
- units of information.

### `SBGNArc`

Each arc stores:

- `arc_id` and `arc_class`;
- `source` and `target` glyph IDs; and
- `spline_points`, an ordered list of `(x, y)` coordinates.

You can inspect one object at a time:

```python
first_glyph = next(iter(pathway.glyphs.values()))
print(first_glyph.glyph_id, first_glyph.glyph_class, first_glyph.label)

if pathway.arcs:
    first_arc = pathway.arcs[0]
    print(first_arc.arc_class, first_arc.source, first_arc.target)
```

## Understand the SBGN node table

`sbgn_to_df()` returns these columns:

| Column | Meaning |
| --- | --- |
| `entry_id` | glyph ID |
| `name` | glyph ID used as the node name |
| `type` | simplified Pathview Plus node type |
| `x`, `y` | center position |
| `width`, `height` | glyph size |
| `bgcolor` | starting background color |
| `label` | display label, or glyph ID when no label is stored |
| `shape` | simplified drawing shape |
| `reaction` | reaction field in the unified table |
| `component` | component field in the unified table |
| `size` | node-size field in the unified table |
| `kegg_names` | glyph ID used by the unified mapping table |

Common SBGN glyph classes are simplified as follows:

| SBGN glyph class | Simplified `type` |
| --- | --- |
| `macromolecule`, `nucleic acid feature`, `complex`, `multimer`, `unspecified entity` | `gene` |
| `simple chemical` | `compound` |
| `process`, `omitted process`, `uncertain process`, `association`, `dissociation`, `phenotype` | `process` |
| `compartment` | `compartment` |
| `submap` | `map` |
| `and`, `or`, `not` | `operator` |

## Use the class reference dictionaries

Pathview Plus includes two dictionaries that translate SBGN class names into
short descriptions:

```python
from pathview import SBGN_ARC_CLASSES, SBGN_GLYPH_CLASSES


print(SBGN_GLYPH_CLASSES["simple chemical"])
print(SBGN_ARC_CLASSES["inhibition"])
```

`SBGN_GLYPH_CLASSES` contains:

- `macromolecule`, `simple chemical`, `nucleic acid feature`, `complex`,
  `multimer`, and `unspecified entity`;
- `process`, `omitted process`, `uncertain process`, `association`,
  `dissociation`, and `phenotype`;
- `compartment` and `submap`; and
- `and`, `or`, and `not`.

`SBGN_ARC_CLASSES` contains:

- `production` and `consumption`;
- `catalysis` and `modulation`;
- `stimulation`, `inhibition`, and `necessary stimulation`; and
- `logic arc`.

These dictionaries are useful for labels, summaries, and custom renderers.

## Keep the two workflows clear

| Goal | Starting point | Main tool |
| --- | --- | --- |
| make a data-colored KEGG pathway | pathway ID plus gene, KO, or compound table | `pathview()` |
| inspect KEGG XML objects | local KGML file | `parse_kgml()` |
| inspect another database's SBGN objects | local SBGN-ML file | `parse_sbgn()` |
| make a custom table from SBGN glyphs | parsed `SBGNPathway` | `sbgn_to_df()` |

This separation lets beginners keep using the short KEGG workflow while
advanced users assemble database-specific parsing and visualization steps.

[<- Previous: Use the KEGG tools](19-kegg-tools.md) | [Home](index.md) | [Next: Highlight a finished pathway ->](21-highlighting.md)
