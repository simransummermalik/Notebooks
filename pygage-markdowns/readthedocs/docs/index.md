# PyGAGE: a step-by-step guide

This guide teaches gene-set enrichment with PyGAGE from the beginning. It
assumes that you are new to Python, gene-set enrichment, or both.

The first five pages explain every word and run a complete practice analysis.
Later pages show how to use real expression matrices, differential-expression
tables, pre-ranked results, KEGG, KEGG Orthology, Gene Ontology, Reactome,
MSigDB, plots, notebooks, and the command line.

## The whole idea in one line

```text
gene measurements + groups of related genes -> ranked enriched gene sets
```

PyGAGE asks whether genes belonging to the same biological group tend to show
coordinated values relative to the background of measured genes.

## Start here if you have never coded

Read these pages in order:

1. [Learn the words used in the guide](01-before-you-begin.md).
2. [Install the exact PyGAGE version used here](02-install.md).
3. [Run a complete practice enrichment](03-first-enrichment.md).
4. [Understand what the first result means](04-understand-enrichment.md).
5. [Choose the route matching your own data](05-choose-input.md).

Each code block is complete and each filename is stated before it is used.

## Choose your input route

| I have | Start here |
| --- | --- |
| no data yet; I want to practice | [Run the first enrichment](03-first-enrichment.md) |
| a genes-by-samples expression matrix | [Understand an expression matrix](06-expression-matrix.md) |
| a matrix of already calculated gene changes | [Run the one-call workflow](10-one-call-gage.md) |
| a DESeq2, edgeR, or limma result table | [Use a differential-expression table](12-de-tables.md) |
| a ranked gene-to-score list | [Use pre-ranked data](13-preranked.md) |
| a pandas DataFrame or AnnData object | [Use pandas or AnnData](14-pandas-anndata.md) |
| KO identifiers from a genome or metagenome analysis | [Use KEGG Orthology data](16-kegg-orthology.md) |

## Choose your gene-set source

| I need | Open |
| --- | --- |
| organism-specific KEGG pathways | [Download KEGG gene sets](15-kegg.md) |
| species-independent KO pathways or modules | [Use KEGG Orthology](16-kegg-orthology.md) |
| Gene Ontology terms | [Build Gene Ontology sets](17-gene-ontology.md) |
| Reactome, MSigDB, or another GMT file | [Use other gene-set sources](18-other-gene-sets.md) |

## Choose your goal

| I want to | Open |
| --- | --- |
| understand p-values, q-values, and direction | [Understand every result column](19-results.md) |
| choose a test or comparison type | [Choose statistical settings](20-statistical-settings.md) |
| add effects, leading-edge genes, or permutations | [Use advanced options](21-advanced-options.md) |
| filter, group, compare, or export results | [Filter, group, compare, and export](22-group-overlap.md) |
| make a bubble plot, heatmap, or enrichment curve | [Make enrichment plots](23-visualization.md) |
| run PyGAGE from Terminal | [Use the command line](24-command-line.md) |
| work one notebook cell at a time | [Use a Jupyter notebook](25-notebooks.md) |
| follow a real-data project structure | [Follow a real-data workflow](26-real-dataset.md) |
| look up an exact function or default | [Open the complete Python API](30-api-reference.md) |

## What this guide covers

The guide is based on PyGAGE 1.2.1 from the official
[RAW Lab PyGAGE repository](https://github.com/raw-lab/pygage), reviewed at
source commit `486e0b800778ec03fe03764aa9dccbe904cfd70b`. It covers:

- the high-level `gage()` workflow;
- the staged `GAGEPreparation` and `GAGEAnalysis` workflow;
- all supported input adapters;
- all gene-set loaders and KEGG/GO retrieval tools;
- all analysis settings and result fields;
- redundancy grouping and result comparison;
- all plotting helpers;
- all four command-line subcommands;
- compute and thread configuration;
- every public Python class and function; and
- citation, reproducibility, and support.

## A scientific reminder

PyGAGE reports statistical enrichment. Interpretation still depends on the
experiment, preprocessing, identifiers, comparison design, gene-set source,
and biological context. Save those details with every result table and figure.

## Project links

- [PyGAGE source code](https://github.com/raw-lab/pygage)
- [PyGAGE issues and questions](https://github.com/raw-lab/pygage/issues)
- [PyGAGE documentation](https://pygage.readthedocs.io)
- [PyGAGE package page](https://pypi.org/project/PyGAGE/)

[Start with page 1: Before you begin ->](01-before-you-begin.md)
