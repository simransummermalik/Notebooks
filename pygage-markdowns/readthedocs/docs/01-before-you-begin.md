# Before you begin

*Page 1 of 31*

This page introduces the words and decisions used throughout the guide. You do
not need previous Python or gene-set enrichment experience.

## What PyGAGE does

PyGAGE studies groups of related genes. A group may represent a pathway,
biological process, cellular location, molecular function, or another
research-defined gene set.

The basic workflow is:

```text
measurements for individual genes
              +
lists of genes belonging to biological groups
              |
              v
statistical enrichment results for each group
```

The result helps you find groups whose members show coordinated measurements
relative to the measured-gene background.

## Five words to know

### Gene

A gene is a section of DNA carrying biological information. Analysis programs
usually represent a gene with an identifier such as an Entrez Gene ID, gene
symbol, Ensembl ID, or KO identifier.

### Gene set

A gene set is a named group of gene identifiers:

```python
{
    "Growth pathway": ["1", "2", "3", "4"],
    "Stress pathway": ["7", "8", "9", "10"],
}
```

The name is on the left. The member genes are inside the list on the right.

### Measurement

A measurement is a number attached to a gene. Examples include expression,
log2 fold change, a differential-expression statistic, abundance change, or a
pre-ranked score.

### Enrichment

Enrichment asks whether genes in the same set show a coordinated pattern
relative to the background of measured genes.

### Direction

PyGAGE can report two directions:

- `greater` for sets tending toward higher or more positive values; and
- `less` for sets tending toward lower or more negative values.

The biological meaning of higher and lower comes from the measurement supplied
to the analysis.

## What a result looks like

Each result row describes one gene set in one direction:

| gene_set | set_size | stat_mean | p_val | q_val | direction |
| --- | ---: | ---: | ---: | ---: | --- |
| Growth pathway | 4 | 2.27 | 0.0098 | 0.029 | greater |

The first analysis on page 3 creates a table like this. Page 19 explains every
column in detail.

## The two inputs must use matching identifiers

Gene measurements and gene sets connect through identifiers:

```text
measurement gene ID == gene-set member ID
```

For example, a table using Entrez IDs should be paired with gene sets using
Entrez IDs. A KO-level table should be paired with KO gene sets.

Identifiers are stored as text so letters and leading zeroes remain part of
the ID.

## Choose the biological comparison first

Before running a real analysis, write down:

1. what was measured;
2. which samples form the reference group;
3. which samples form the comparison group;
4. what a positive value means;
5. what a negative value means;
6. which identifier system is used; and
7. which gene-set collection answers the biological question.

These decisions determine how the input is prepared and how the result is
interpreted.

## Common input routes

| Starting point | What PyGAGE receives |
| --- | --- |
| raw expression matrix | gene rows plus reference and sample columns |
| prepared change matrix | gene rows plus already calculated comparison columns |
| DESeq2, edgeR, or limma table | gene IDs plus log2 fold change or a statistic |
| pre-ranked analysis | gene IDs plus one numeric score |
| genome or metagenome annotation | KO IDs plus numeric measurements |

Page 5 helps you select one route.

## What you need for the guide

- a computer with internet access for installation and database downloads;
- Python 3.8 or newer;
- a plain-text editor or code editor;
- Terminal on macOS or Linux, or PowerShell on Windows; and
- a folder where scripts, input tables, and results can stay together.

The first practice analysis creates its data inside the script, so you can
learn the workflow before preparing your own files.

## Your learning route

The pages are intentionally staged:

```text
learn the words
      |
      v
install PyGAGE
      |
      v
run a tiny complete analysis
      |
      v
understand the result
      |
      v
choose the route for your real data
```

[Home](index.md) | [Next: Install PyGAGE ->](02-install.md)
