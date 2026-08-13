# Recipe book

*Page 13 of 24*

Choose the row closest to your project and open its complete tutorial.

## Choose by input

| My first column contains | My numeric columns contain | Tutorial |
| --- | --- | --- |
| Entrez Gene IDs | one gene measurement | [Map one gene measurement](06-one-gene-condition.md) |
| Entrez Gene IDs | several conditions or time points | [Compare several gene conditions](07-multiple-gene-conditions.md) |
| KO IDs such as `K02586` | functional measurements | [Map KEGG Orthology data](08-kegg-orthology.md) |
| compound IDs such as `C00031` | compound measurements | [Map compounds](09-compounds-and-multiomics.md#part-a-map-compounds) |
| genes and compounds in two tables | one measurement for each data type | [Map genes and compounds together](09-compounds-and-multiomics.md#part-b-map-genes-and-compounds-together) |
| gene symbols, Ensembl IDs, or UniProt IDs | one or more gene measurements | [Convert gene identifiers](16-identifier-conversion.md#convert-gene-identifiers) |
| PubChem or ChEBI IDs | one or more compound measurements | [Convert compound identifiers](16-identifier-conversion.md#convert-compound-identifiers) |

## Choose by task

| I want to | Tutorial |
| --- | --- |
| make my first small example | [Make your first pathway](03-first-pathway.md) |
| load a TSV file | [Prepare your own data](04-prepare-your-data.md) |
| find a pathway and species code | [Choose a pathway and species](05-choose-a-pathway.md) |
| choose a color palette and limits | [Choose colors and read the image](10-colors-and-images.md) |
| make several pathway images | [Run several pathways](11-many-pathways.md) |
| work in Jupyter cells | [Use Pathview Plus in a notebook](12-use-a-notebook.md) |
| save PNG, SVG, or PDF output | [Choose an output format](15-output-formats.md) |
| practice before I have my own table | [Simulate demonstration data](17-simulate-and-summarize.md) |
| combine repeated IDs that map to one node | [Choose an aggregation rule](17-simulate-and-summarize.md#combine-repeated-identifiers) |
| use Terminal instead of a Python script | [Use the command line](18-command-line.md) |
| understand downloaded and cached KEGG files | [Download and inspect KEGG pathways](19-kegg-tools.md) |
| inspect KGML pathway nodes and relations | [Parse a downloaded KGML file](19-kegg-tools.md#inspect-a-kgml-file) |
| inspect an SBGN-ML pathway | [Work with SBGN and pathway databases](20-sbgn-and-databases.md) |
| highlight a node, edge, or ordered path | [Highlight pathway elements](21-highlighting.md) |
| make custom SVG elements or curves | [Build curves and SVG elements](22-curves-and-svg.md) |
| look up an exact function or default | [Use the complete API reference](23-api-reference.md) |
| write a caption, cite the tool, or ask for help | [Cite, report, and get support](24-citation-and-support.md) |

## The table pattern for each recipe

### One gene measurement

```text
entrez_id | log2_fold_change
```

### Several gene conditions

```text
entrez_id | Control | Treatment_A | Treatment_B
```

### KO data

```text
ko_id | difference
```

### Compound data

```text
compound_id | log2_fold_change
```

### Gene symbols

```text
symbol | log2_fold_change
```

### A command-line TSV file

```text
entrez_id<TAB>log2_fold_change
```

The characters `<TAB>` mean one tab between the two fields.

## Choose by where the values came from

| Starting analysis | Value that can become a pathway color | Suggested route |
| --- | --- | --- |
| differential transcriptomics | log2 fold change, statistic, or score per gene | [One gene condition](06-one-gene-condition.md) or [several conditions](07-multiple-gene-conditions.md) |
| proteomics | abundance change or score attached to gene-compatible IDs | [Prepare the table](04-prepare-your-data.md), then [convert IDs](16-identifier-conversion.md) |
| variant analysis | a documented numeric gene-level summary | [Prepare the table](04-prepare-your-data.md) |
| metabolomics | abundance or abundance change per compound | [Compound workflow](09-compounds-and-multiomics.md) |
| pathway enrichment | selected pathway IDs plus a separate gene-value table | [Run several pathways](11-many-pathways.md#use-pathway-ids-from-an-enrichment-table) |
| genome or metagenome annotation | KO abundance, score, or group difference | [MetaCerberus-to-KO workflow](08-kegg-orthology.md#from-metacerberus-results-to-this-table) |

## Four choices every recipe needs

Before running a recipe, write down:

1. **Data:** which table contains the IDs and values?
2. **Pathway:** which five-digit KEGG pathway number will you use?
3. **Species:** which organism code, or `ko`, matches the data?
4. **Output name:** what short suffix describes the analysis?

When those four choices are clear, open the matching tutorial and replace its
teaching values with your own.

[<- Previous: Use Pathview Plus in a notebook](12-use-a-notebook.md) | [Home](index.md) | [Next: Glossary ->](14-glossary.md)
