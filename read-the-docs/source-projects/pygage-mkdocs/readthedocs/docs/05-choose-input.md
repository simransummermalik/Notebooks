# Choose your input route

*Page 5 of 31*

PyGAGE accepts several common analysis formats. Choose one route based on the
table or object you already have.

## Route A: raw expression matrix

Choose this route when your table contains one row per gene and one column per
sample:

```text
gene_id | reference_1 | reference_2 | treatment_1 | treatment_2
```

Continue with:

1. [Understand an expression matrix](06-expression-matrix.md)
2. [Choose reference and sample columns](07-reference-and-sample.md)
3. [Read and prepare the matrix](08-prepare-expression.md)
4. [Run the one-call workflow](10-one-call-gage.md)

## Route B: prepared change matrix

Choose this route when each numeric column is already a gene-level comparison:

```text
gene_id | change_1 | change_2
```

Continue with [Run the one-call workflow](10-one-call-gage.md) and set:

```python
prepared=True
```

The practice table on page 3 followed this route.

## Route C: DESeq2, edgeR, or limma table

Choose this route when a differential-expression program produced columns such
as:

```text
gene_id | log2FoldChange | stat | pvalue | padj
```

Continue with
[Use a differential-expression table](12-de-tables.md).

PyGAGE can select either a log2 fold-change column or a statistical-score
column.

## Route D: pre-ranked genes

Choose this route when every gene already has one score:

```text
gene_id | score
```

Continue with [Use pre-ranked data](13-preranked.md).

## Route E: pandas DataFrame

Choose this route when the table already exists in Python as a pandas
DataFrame. Continue with [Use pandas or AnnData](14-pandas-anndata.md).

PyGAGE converts the table at the input boundary and returns Polars result
tables.

## Route F: AnnData

Choose this route when samples and genes are stored in an AnnData object,
commonly loaded from an `.h5ad` file.

Continue with [Use pandas or AnnData](14-pandas-anndata.md).

## Route G: KO-level functional data

Choose this route when the first column contains KEGG Orthology identifiers
such as:

```text
K00844
K12407
K02586
```

This route is useful for genome, metagenome, virome, phage, and other
species-independent functional analyses.

Continue with [Use KEGG Orthology data](16-kegg-orthology.md).

## Choose the gene-set source separately

The input values and gene sets are two separate choices:

```text
input format = how gene measurements are stored
gene-set source = which biological groups are tested
```

| Biological grouping | Tutorial |
| --- | --- |
| KEGG pathways for one organism | [KEGG](15-kegg.md) |
| KEGG Orthology pathways or modules | [KEGG Orthology](16-kegg-orthology.md) |
| Gene Ontology terms | [Gene Ontology](17-gene-ontology.md) |
| Reactome pathways | [Reactome](18-other-gene-sets.md#reactome) |
| MSigDB collections | [MSigDB](18-other-gene-sets.md#msigdb) |
| any valid GMT file | [GMT](18-other-gene-sets.md#load-any-gmt-file) |

## Identifier checklist

Before continuing, confirm:

- the gene identifier is in the first column or a clearly named column;
- all identifiers are stored as text;
- the same identifier system is used by the measurements and gene sets;
- duplicate-gene handling is part of the preparation plan;
- numeric columns have a documented meaning; and
- missing values have been reviewed.

## Analysis-design checklist

For a raw matrix, also write down:

- reference sample columns;
- comparison sample columns;
- paired or unpaired design;
- whether input values are already log-transformed; and
- whether each sample should remain separate or groups should be averaged.

Pages 6–8 explain each choice.

[<- Previous: Understand the first result](04-understand-enrichment.md) | [Home](index.md) | [Next: Understand an expression matrix ->](06-expression-matrix.md)
