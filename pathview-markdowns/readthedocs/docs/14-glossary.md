# Glossary

*Page 14 of 24*

This glossary explains common words used throughout the Pathview Plus guide. The definitions are written for readers who are new to Python, pathway analysis, or both.

## Abundance

A numeric measurement of how much of a compound was found in a sample. Pathview Plus can use an abundance value, or a change in abundance, to color a compound on a pathway.

## Aggregation

Combining several values into one result. When several input IDs map to one
pathway node, Pathview Plus can combine them with a sum, mean, median, maximum,
or another `node_sum` rule.

## API

An application programming interface. In this guide, the Pathview Plus API is
the set of Python functions, classes, and settings that a script can import.

## Arc

A connection between two glyphs in an SBGN pathway. An arc can represent an
interaction such as production, consumption, stimulation, or inhibition.

## Batch

A group of pathway jobs run by one script. A Python loop can make a batch of pathway pictures from the same data table.

## Bézier curve

A smooth curve calculated from endpoints and control points. Pathview Plus
includes quadratic and cubic Bézier helpers for custom visualization work.

## Cache

Locally saved files that can be reused. The `kegg_dir` folder stores downloaded
KEGG pathway files so a later run can use the same local material.

## ChEBI

Chemical Entities of Biological Interest, a database and identifier system for
chemical compounds. Pathview Plus can map ChEBI compound IDs to KEGG compound
IDs.

## CLI

A command-line interface. It lets a user run Pathview Plus by typing a command
in Terminal instead of writing a complete Python script.

## Color bin

One level in a color scale. More bins create finer color steps; fewer bins
create broader color groups.

## Column

A vertical part of a table. In a Pathview Plus input table, the first column contains IDs. Each column after it contains numeric results.

## Compound

A small molecule, metabolite, or other chemical shown on a pathway. KEGG compound IDs usually begin with `C`, such as `C00031`.

## Condition

One sample, group, treatment, or time point in an experiment. Each condition can be stored in its own numeric column.

## DataFrame

A table used inside Python. This guide uses a package called Polars to create DataFrames.

## Edge

A connection between two pathway nodes. It can represent a relationship,
reaction direction, activation, inhibition, or another type of link.

## Ensembl ID

An identifier from the Ensembl genome resource. Pathview Plus identifier tools
can connect supported Ensembl gene IDs to Entrez Gene IDs.

## Entrez gene ID

A number that identifies a gene in the NCBI Gene database. For example, the human gene **EGFR** has Entrez ID `1956`.

## Fold change

A number that compares a measurement between two groups. It describes how much the measurement changed.

## Gene

A section of DNA that carries biological information. Pathways show how the products of genes take part in biological processes.

## Gene expression

A measurement related to how actively a gene is being used in a cell or sample. Gene expression results can be placed on pathway gene boxes.

## Gene symbol

A short, human-readable gene label such as `EGFR`, `TP53`, or `KRAS`. The
`gene_idtype="SYMBOL"` setting identifies a first column containing gene
symbols.

## Glyph

A visual object in an SBGN pathway, such as a gene product, compound, process,
or compartment.

## Identifier (ID)

A name or code that points to one gene, compound, pathway, or ortholog group. Examples include Entrez gene IDs, KEGG compound IDs, and KO IDs.

## KEGG

The Kyoto Encyclopedia of Genes and Genomes. KEGG provides pathway diagrams, pathway IDs, organism codes, gene information, compounds, and orthology groups.

## KEGG compound ID

A KEGG code that identifies a compound. It begins with `C` followed by five digits, such as `C00031` for D-glucose.

## KEGG native picture

The familiar pathway image supplied by KEGG. Setting `kegg_native=True` places your colors on this picture.

## KGML

KEGG Markup Language, the XML format that describes the nodes, positions,
relations, and reactions in a KEGG pathway.

## KEGG Orthology (KO)

A KEGG system that groups genes with the same general function across organisms. A KO ID begins with `K`, such as `K02586`.

## JupyterLab

A browser-based program for creating and running notebooks. It lets you run
Python one cell at a time.

## Log2 fold change

A fold change written on a base-2 logarithmic scale. Positive and negative values show opposite directions of change, and zero represents no change between the compared groups.

## Map or mapping

To connect an ID in your table to the matching gene or compound on a pathway. A mapped item can receive a color from your numeric data.

## Mapping table

A table that records how input identifiers connect to another identifier
system or to pathway nodes. The dictionaries returned by `pathview()` include
mapped gene and compound node tables.

## MetaCerberus

A functional-annotation workflow that can assign KEGG Orthology functions to
genes in genomes or metagenomes. Summarized KO values can be visualized on a
KEGG Orthology pathway.

## MetaCyc

A curated database of metabolic pathways. Pathview Plus includes advanced
helpers for MetaCyc pathway downloads.

## Multi-omics

An analysis that combines more than one type of biological measurement. In
this guide, a multi-omics pathway can display gene and compound values
together.

## Node

One object on a pathway diagram, such as a gene box, compound circle, process,
or group. Several input identifiers can sometimes map to the same node.

## `node_sum`

The Pathview Plus setting that chooses how several values mapping to one node
are combined. Choices include `sum`, `mean`, `median`, `max`, `max_abs`, and
`random`.

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

## PANTHER

A biological classification system that includes pathway information.
Pathview Plus includes advanced helpers for working with PANTHER pathway
files.

## PDF

Portable Document Format. Pathview Plus graph-layout output can be saved as a
PDF vector figure.

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

## PubChem

A public chemical-information resource and identifier system. Pathview Plus
can map supported PubChem compound IDs to KEGG compound IDs.

## Reactome

A curated pathway knowledgebase. Pathview Plus includes advanced functions for
listing Reactome pathways and downloading pathway files.

## Renderer

Code that turns pathway data, positions, colors, and labels into a finished
image or vector file. Pathview Plus has native KEGG, graph, and SVG renderers.

## Row

A horizontal part of a table. Each input row usually contains one ID and its numeric value or values.

## Species

An organism, such as human, mouse, rat, or a bacterium. The `species` setting tells Pathview Plus which organism's pathway to use.

## SBGN

Systems Biology Graphical Notation, a standard visual language for biological
networks and pathways.

## SBGN-ML

The XML file format used to store an SBGN diagram. Pathview Plus can parse an
SBGN-ML file into pathway objects and a DataFrame.

## SMPDB

The Small Molecule Pathway Database. Pathview Plus includes advanced helpers
for working with SMPDB pathway files.

## Spline

A smooth line built from several points or curve segments. Pathview Plus
provides spline helpers for custom pathway graphics.

## String

Text stored by Python. IDs are kept as strings so every character, including leading letters or zeros, stays part of the ID.

## Terminal

An application where you type commands. You can use it to install Pathview Plus, open Jupyter, or run a Python file.

## TSV file

A **tab-separated values** file. It stores a table in plain text, with a tab between each column. Pathview Plus can read TSV data with Polars.

## SVG

Scalable Vector Graphics, a text-based vector image format. SVG pathway
figures can be enlarged without becoming pixelated and can be edited in vector
graphics software.

## UniProt ID

An identifier for a protein record in UniProt. Pathview Plus identifier tools
can connect supported UniProt IDs to Entrez Gene IDs.

## Vector image

An image stored as shapes, paths, and text instead of a fixed grid of pixels.
SVG and many PDF figures are vector formats.

## Working directory

The folder a terminal or Python session is currently using. A short filename such as `gene_data.tsv` is looked up inside this folder.

---

[<- Previous: Recipe book](13-recipe-book.md) | [Home](index.md) | [Next: Choose PNG, SVG, or PDF output ->](15-output-formats.md)
