# Glossary

*Page 14 of 14*

This glossary explains common words used throughout the Pathview Plus guide. The definitions are written for readers who are new to Python, pathway analysis, or both.

## Abundance

A numeric measurement of how much of a compound was found in a sample. Pathview Plus can use an abundance value, or a change in abundance, to color a compound on a pathway.

## Batch

A group of pathway jobs run by one script. A Python loop can make a batch of pathway pictures from the same data table.

## Column

A vertical part of a table. In a Pathview Plus input table, the first column contains IDs. Each column after it contains numeric results.

## Compound

A small molecule, metabolite, or other chemical shown on a pathway. KEGG compound IDs usually begin with `C`, such as `C00031`.

## Condition

One sample, group, treatment, or time point in an experiment. Each condition can be stored in its own numeric column.

## DataFrame

A table used inside Python. This guide uses a package called Polars to create DataFrames.

## Entrez gene ID

A number that identifies a gene in the NCBI Gene database. For example, the human gene **EGFR** has Entrez ID `1956`.

## Fold change

A number that compares a measurement between two groups. It describes how much the measurement changed.

## Gene

A section of DNA that carries biological information. Pathways show how the products of genes take part in biological processes.

## Gene expression

A measurement related to how actively a gene is being used in a cell or sample. Gene expression results can be placed on pathway gene boxes.

## Identifier (ID)

A name or code that points to one gene, compound, pathway, or ortholog group. Examples include Entrez gene IDs, KEGG compound IDs, and KO IDs.

## KEGG

The Kyoto Encyclopedia of Genes and Genomes. KEGG provides pathway diagrams, pathway IDs, organism codes, gene information, compounds, and orthology groups.

## KEGG compound ID

A KEGG code that identifies a compound. It begins with `C` followed by five digits, such as `C00031` for D-glucose.

## KEGG native picture

The familiar pathway image supplied by KEGG. Setting `kegg_native=True` places your colors on this picture.

## KEGG Orthology (KO)

A KEGG system that groups genes with the same general function across organisms. A KO ID begins with `K`, such as `K02586`.

## JupyterLab

A browser-based program for creating and running notebooks. It lets you run
Python one cell at a time.

## Log2 fold change

A fold change written on a base-2 logarithmic scale. Positive and negative values show opposite directions of change, and zero represents no change between the compared groups.

## Map or mapping

To connect an ID in your table to the matching gene or compound on a pathway. A mapped item can receive a color from your numeric data.

## Notebook

A file that holds Python code in small runnable cells. A Jupyter notebook uses
the `.ipynb` filename ending.

## Numeric value

A number that Pathview Plus turns into a color. Examples include log2 fold change, expression, score, and abundance change.

## Organism code

A short KEGG code for a species. Examples include `hsa` for human, `mmu` for mouse, and `rno` for rat.

## Package

Reusable Python software installed into a project. Pathview Plus and Polars are
packages used in this guide.

## Output

The files made by a program. A Pathview Plus output includes the colored pathway picture and the pathway files used to create it.

## Pathview Plus

A Python tool that places gene and compound data on pathway diagrams.

## Pathway

A diagram of connected biological events. A pathway can show signaling, metabolism, the cell cycle, disease processes, and many other biological systems.

## Pathway ID

A code that identifies one KEGG pathway. For example, `04151` identifies the PI3K-Akt signaling pathway. A species prefix can be added, such as `hsa04151` for the human pathway.

## PNG

An image file format. Native KEGG pathway pictures made in this guide are saved as PNG files.

## Polars

A Python package for working with tables. In this guide it is imported with `import polars as pl`.

## Python

The programming language used to run Pathview Plus.

## Row

A horizontal part of a table. Each input row usually contains one ID and its numeric value or values.

## Species

An organism, such as human, mouse, rat, or a bacterium. The `species` setting tells Pathview Plus which organism's pathway to use.

## String

Text stored by Python. IDs are kept as strings so every character, including leading letters or zeros, stays part of the ID.

## Terminal

An application where you type commands. You can use it to install Pathview Plus, open Jupyter, or run a Python file.

## TSV file

A **tab-separated values** file. It stores a table in plain text, with a tab between each column. Pathview Plus can read TSV data with Polars.

## Working directory

The folder a terminal or Python session is currently using. A short filename such as `gene_data.tsv` is looked up inside this folder.

---

[<- Previous: Recipe book](13-recipe-book.md) | [Home](../README.md)
