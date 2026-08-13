# New to PyGAGE?

This short guide is for readers who are new to Python, gene-set enrichment, or
both. It introduces the main ideas, runs one complete practice analysis, and
explains how to prepare a raw expression table.

You do not need to understand the statistical formulas before starting.

## The whole idea

PyGAGE combines two kinds of information:

```text
measurements for individual genes
                +
named groups of related genes
                |
                v
enrichment results for each group
```

Instead of reviewing thousands of genes one at a time, you can ask whether the
genes in a pathway or other biological group tend to change together.

## Six useful words

| Word | Plain-language meaning |
| --- | --- |
| **gene** | A biological feature represented by an identifier such as `TP53`, `7157`, or `K00844`. |
| **gene set** | A named list of related gene identifiers. |
| **measurement** | A number attached to a gene, such as expression, log2 fold change, or a ranked score. |
| **enrichment** | Evidence that the measurements for one gene set differ from the measured-gene background. |
| **greater** | The set tends toward higher or more positive measurements. |
| **less** | The set tends toward lower or more negative measurements. |

The meaning of “greater” and “less” comes from your input. For example, if a
positive number means higher expression after treatment, a `greater` result
points toward higher values after treatment.

## The two inputs must match

Every analysis needs:

1. a table of gene measurements; and
2. gene sets containing the biological groups to test.

The identifiers in those two inputs must use the same system:

```text
measurement ID == gene-set member ID
```

For example, gene symbol `TP53`, Entrez ID `7157`, and Ensembl ID
`ENSG00000141510` identify the same gene in different systems, but they are not
the same text. PyGAGE matches identifiers exactly.

{doc}`Prepare your data <prepare-data>` shows how to check matching and convert
between gene symbols and Entrez IDs.

## Choose the route that matches your data

| What you already have | Where to continue |
| --- | --- |
| No data yet; you want to learn the workflow | {doc}`Run your first analysis <first-analysis>` |
| Raw expression values, with genes in rows and samples in columns | {doc}`Prepare your data <prepare-data>` |
| Values that are already gene-level changes | {doc}`Run your first analysis <first-analysis>` |
| A DESeq2, edgeR, or limma result table | {doc}`Inputs <../guide/inputs>` |
| One ranked score for every gene | {doc}`Inputs <../guide/inputs>` |
| A pandas DataFrame or AnnData object | {doc}`Inputs <../guide/inputs>` |
| KEGG, KO, GO, Reactome, MSigDB, or GMT gene sets | {doc}`Gene-set sourcing <../guide/genesets>` |

Input format and gene-set source are separate choices. A DESeq2 result, for
example, can be analyzed with KEGG, Gene Ontology, or another collection whose
identifiers match the DESeq2 table.

## Before analyzing real data

Write down:

- what each number in the input represents;
- which samples are the reference group;
- which samples are being compared with that reference;
- what a positive and negative value mean;
- which gene-identifier system is used;
- where the gene sets came from; and
- which significance rule will be used.

These notes make the result easier to interpret and the analysis easier to
repeat.

## A simple learning path

1. Follow the official {doc}`installation instructions <../installation>`.
2. Complete {doc}`your first analysis <first-analysis>`.
3. Read {doc}`prepare your data <prepare-data>` before using a raw matrix.
4. Learn about the available {doc}`inputs <../guide/inputs>` and
   {doc}`gene-set sources <../guide/genesets>`.
5. Use {doc}`understanding the results <../guide/results>` to interpret a real
   result table.

The existing {doc}`quickstart <../quickstart>` provides a second example using
the real GAGE demonstration data bundled with PyGAGE.

```{toctree}
:hidden:
:maxdepth: 1

first-analysis
prepare-data
```
