# Pathview Plus: a walkthrough guide

This guide teaches you how to place biological measurements on a KEGG pathway
with Pathview Plus.

You do not need to know Pathview Plus, Polars, or much Python before you begin.
The pages are numbered so you can read them in order. Navigation links connect
the pages and return to this home page.

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
- several pathway images in one run.

## Choose your route

You can read every page in order, or jump to the table that matches your data:

| I have | Start here |
| --- | --- |
| Entrez Gene IDs and one value column | [Map one gene measurement](docs/06-one-gene-condition.md) |
| Entrez Gene IDs and several conditions | [Compare several gene conditions](docs/07-multiple-gene-conditions.md) |
| KO IDs beginning with `K` | [Map KEGG Orthology data](docs/08-kegg-orthology.md) |
| compound IDs beginning with `C` | [Map compounds](docs/09-compounds-and-multiomics.md#part-a-map-compounds) |
| gene and compound tables | [Map both data types](docs/09-compounds-and-multiomics.md#part-b-map-genes-and-compounds-together) |

## Read the guide in order

1. [Before you begin](docs/01-before-you-begin.md)
2. [Install Pathview Plus](docs/02-install.md)
3. [Make your first pathway](docs/03-first-pathway.md)
4. [Prepare your own data](docs/04-prepare-your-data.md)
5. [Choose a pathway and species](docs/05-choose-a-pathway.md)
6. [Map one gene measurement](docs/06-one-gene-condition.md)
7. [Compare several gene conditions](docs/07-multiple-gene-conditions.md)
8. [Map KEGG Orthology data](docs/08-kegg-orthology.md)
9. [Map compounds and multi-omics data](docs/09-compounds-and-multiomics.md)
10. [Choose colors and read the image](docs/10-colors-and-images.md)
11. [Run several pathways](docs/11-many-pathways.md)
12. [Use Pathview Plus in a notebook](docs/12-use-a-notebook.md)
13. [Choose a ready-made recipe](docs/13-recipe-book.md)
14. [Look up a word in the glossary](docs/14-glossary.md)

## What you need

- a computer with internet access;
- Python 3.10 or newer;
- a small table of biological identifiers and numbers; and
- a KEGG pathway that matches your biological question.

The examples use Pathview Plus 2.0.2, Polars DataFrames, KEGG pathway IDs,
Entrez Gene IDs, KO IDs, and KEGG compound IDs. Each of those terms is
introduced before you need it.

## A note for researchers

The color meaning always comes from the measurement you provide. For example,
if your column contains log2 fold change, the low-end color represents a
negative log2 fold change and the high-end color represents a positive log2
fold change. Record the column name, units, comparison, and color limits with
every figure.

## Project links

- [Pathview Plus source code](https://github.com/raw-lab/pathview-plus)
- [Pathview Plus on PyPI](https://pypi.org/project/pathview-plus/)
- [KEGG PATHWAY](https://www.kegg.jp/kegg/pathway.html)

[Start with page 1: Before you begin ->](docs/01-before-you-begin.md)
