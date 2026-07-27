# Pathview Plus: a walkthrough guide

This guide teaches you how to place biological measurements on pathway
diagrams with Pathview Plus. It begins with a small KEGG example, explains
every part, and then introduces the program's additional tools one page at a
time.

You do not need to know Pathview Plus, Polars, or much Python before you begin.
The pages are numbered so you can read them in order. Navigation links connect
the pages and return to this home page.

The Read the Docs website source is organized in the
[`readthedocs`](readthedocs/) folder.

## The whole idea in one line

```text
your IDs and values + a KEGG pathway -> a colored pathway image
```

The identifier tells Pathview Plus where a measurement belongs. The number
tells Pathview Plus which color to place there.

## What you will learn

By the end, you will know how to make:

- one pathway from gene data;
- a pathway with several conditions;
- a KEGG Orthology, or KO, pathway;
- a pathway with compound data;
- a pathway with genes and compounds together; and
- several pathway images in one run;
- PNG, SVG, and PDF output;
- pathways from several identifier systems;
- command-line and simulated-data workflows; and
- advanced SBGN, highlighting, rendering, and curve workflows.

## Choose your route

You can read every page in order, or jump to the table that matches your data:

| I have | Start here |
| --- | --- |
| Entrez Gene IDs and one value column | [Map one gene measurement](readthedocs/docs/06-one-gene-condition.md) |
| Entrez Gene IDs and several conditions | [Compare several gene conditions](readthedocs/docs/07-multiple-gene-conditions.md) |
| KO IDs beginning with `K` | [Map KEGG Orthology data](readthedocs/docs/08-kegg-orthology.md) |
| compound IDs beginning with `C` | [Map compounds](readthedocs/docs/09-compounds-and-multiomics.md#part-a-map-compounds) |
| gene and compound tables | [Map both data types](readthedocs/docs/09-compounds-and-multiomics.md#part-b-map-genes-and-compounds-together) |
| gene symbols, Ensembl IDs, or UniProt IDs | [Convert gene identifiers](readthedocs/docs/16-identifier-conversion.md) |
| PubChem or ChEBI compound IDs | [Convert compound identifiers](readthedocs/docs/16-identifier-conversion.md#convert-compound-identifiers) |
| no data yet, but I want to practice | [Simulate demonstration data](readthedocs/docs/17-simulate-and-summarize.md) |

## Choose by goal

| I want to | Open |
| --- | --- |
| finish my first pathway | [Make your first pathway](readthedocs/docs/03-first-pathway.md) |
| choose colors and understand the result | [Choose colors and read the image](readthedocs/docs/10-colors-and-images.md) |
| make PNG, SVG, or PDF files | [Choose an output format](readthedocs/docs/15-output-formats.md) |
| run Pathview Plus from Terminal | [Use the command line](readthedocs/docs/18-command-line.md) |
| understand downloaded KEGG files | [Download and inspect KEGG pathways](readthedocs/docs/19-kegg-tools.md) |
| use every public Python function | [Open the complete API reference](readthedocs/docs/23-api-reference.md) |

## Read the guide in order

1. [Before you begin](readthedocs/docs/01-before-you-begin.md)
2. [Install Pathview Plus](readthedocs/docs/02-install.md)
3. [Make your first pathway](readthedocs/docs/03-first-pathway.md)
4. [Prepare your own data](readthedocs/docs/04-prepare-your-data.md)
5. [Choose a pathway and species](readthedocs/docs/05-choose-a-pathway.md)
6. [Map one gene measurement](readthedocs/docs/06-one-gene-condition.md)
7. [Compare several gene conditions](readthedocs/docs/07-multiple-gene-conditions.md)
8. [Map KEGG Orthology data](readthedocs/docs/08-kegg-orthology.md)
9. [Map compounds and multi-omics data](readthedocs/docs/09-compounds-and-multiomics.md)
10. [Choose colors and read the image](readthedocs/docs/10-colors-and-images.md)
11. [Run several pathways](readthedocs/docs/11-many-pathways.md)
12. [Use Pathview Plus in a notebook](readthedocs/docs/12-use-a-notebook.md)
13. [Choose a ready-made recipe](readthedocs/docs/13-recipe-book.md)
14. [Look up a word in the glossary](readthedocs/docs/14-glossary.md)
15. [Choose PNG, SVG, or PDF output](readthedocs/docs/15-output-formats.md)
16. [Convert gene and compound identifiers](readthedocs/docs/16-identifier-conversion.md)
17. [Simulate data and combine repeated identifiers](readthedocs/docs/17-simulate-and-summarize.md)
18. [Use the command line](readthedocs/docs/18-command-line.md)
19. [Download and inspect KEGG pathways](readthedocs/docs/19-kegg-tools.md)
20. [Work with SBGN and other pathway databases](readthedocs/docs/20-sbgn-and-databases.md)
21. [Highlight nodes, edges, and paths](readthedocs/docs/21-highlighting.md)
22. [Build curves and SVG pathway elements](readthedocs/docs/22-curves-and-svg.md)
23. [Look up the complete API](readthedocs/docs/23-api-reference.md)
24. [Cite, report, and get support](readthedocs/docs/24-citation-and-support.md)

## What you need

- a computer with internet access;
- Python 3.10 or newer;
- a small table of biological identifiers and numbers; and
- a KEGG pathway that matches your biological question.

The examples use Pathview Plus 2.0.2 and Polars DataFrames. The main learning
route uses KEGG pathway IDs, Entrez Gene IDs, KO IDs, and KEGG compound IDs.
Later pages introduce the other supported identifiers, pathway formats, and
advanced utilities. Each new term is explained before it is used.

## A note for researchers

The color meaning always comes from the measurement you provide. For example,
if your column contains log2 fold change, the low-end color represents a
negative log2 fold change and the high-end color represents a positive log2
fold change. Record the column name, units, comparison, and color limits with
every figure.

## Project links

- [Pathview Plus source code](https://github.com/raw-lab/pathview-plus)
- [Pathview Plus support and questions](https://github.com/raw-lab/pathview-plus/issues)
- [Pathview Plus on PyPI](https://pypi.org/project/pathview-plus/)
- [KEGG PATHWAY](https://www.kegg.jp/kegg/pathway.html)

[Start with page 1: Before you begin ->](readthedocs/docs/01-before-you-begin.md)

## Preview the documentation website

The website uses MkDocs and is configured for Read the Docs. To preview it
locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r readthedocs/requirements.txt
mkdocs serve --config-file readthedocs/mkdocs.yml
```

Then open `http://127.0.0.1:8000` in a web browser.
