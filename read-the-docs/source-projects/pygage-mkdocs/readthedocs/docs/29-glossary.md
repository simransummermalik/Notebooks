# Glossary

*Page 29 of 31*

Use this page whenever the guide introduces an unfamiliar biology,
statistics, file-format, or Python word. The definitions describe how each
term is used in this PyGAGE guide.

## A

### `1ongroup`

A comparison in which each sample is compared with the mean of all reference
samples. It creates one prepared comparison column for each sample.

### `as.group`

A comparison in which the mean of all sample columns is compared with the mean
of all reference columns. It creates one prepared comparison column.

### AnnData

A data object widely used for annotated expression matrices, especially
single-cell data. AnnData normally stores samples or cells as observations and
genes as variables. Its common file extension is `.h5ad`.

### API

Application programming interface. In this guide, the API is the collection of
PyGAGE functions and classes that Python code can import and call.

### Argument

A value supplied to a function or command. In:

```python
read_matrix("expression.csv")
```

`"expression.csv"` is an argument.

## B

### Background

The measured genes used as the reference distribution for a gene-set test.
Standard PyGAGE uses all measured genes as the background. An advanced analysis
can supply `control_genes`.

### Benjamini-Hochberg adjustment

A multiple-testing procedure used to calculate q-values from p-values. It is
often shortened to **BH**.

### Biological Process

One Gene Ontology domain describing a larger biological program or objective,
such as DNA repair. Its abbreviation is **BP**.

### Bubble plot

A result figure in which location, color, and point size display different
properties of each gene set. PyGAGE's enrichment bubble plot uses
`stat_mean`, `q_val`, and `set_size`.

## C

### Cache

A local saved copy that can be reused. PyGAGE can cache gene-set collections
and KEGG responses to reduce repeated downloads and support reproducible work.

### Cellular Component

One Gene Ontology domain describing where a gene product acts, such as the
nucleus or membrane. Its abbreviation is **CC**.

### Checksum

A short value calculated from file or collection contents. It helps identify
the exact collection used in an analysis.

### Class

A Python object that groups related data and actions. `GAGEAnalysis`,
`GeneSetCollection`, and `EnrichmentPlots` are PyGAGE classes.

### CLI

Command-line interface. The PyGAGE CLI is the `pygage` command used in
Terminal or PowerShell.

### Column

A vertical field in a table. An expression matrix normally has one identifier
column and one numeric column for each sample.

### Comparison

The rule used to calculate changes between reference and sample measurements.
PyGAGE supports paired, unpaired, `as.group`, and `1ongroup` preparation.

### Control gene set

An optional, research-defined collection used as the statistical background
instead of all measured genes.

### CSV

Comma-separated values. A plain-text table format whose columns are separated
by commas. Its usual extension is `.csv`.

## D

### DataFrame

A table object with named columns and rows. PyGAGE primarily returns Polars
DataFrames and also accepts pandas DataFrames at input boundaries.

### DCIS

Ductal carcinoma in situ. The packaged GSE16873 demonstration compares six
DCIS samples with six paired HN samples.

### Differential expression

An analysis that estimates how gene measurements differ between conditions.
DESeq2, edgeR, and limma are common tools that produce
differential-expression tables.

### Direction

Whether a gene set tends toward higher or lower supplied measurements. PyGAGE
uses `greater` and `less`.

### Directory

Another word for a computer folder.

## E

### edgeR

A differential-expression tool whose result tables can be read with
`read_de_table`.

### Effect

The mean prepared change across the matched genes in a set. PyGAGE reports it
in the optional or standard `effect` result column when
`compute_effect=True`.

### Enrichment

Evidence that genes belonging to the same set show a coordinated pattern
relative to the measured-gene background.

### Ensembl ID

A gene identifier beginning with a format such as `ENSG` for human genes.
Input measurements and gene-set members must use compatible identifiers.

### Entrez Gene ID

A numeric identifier assigned by NCBI Gene. PyGAGE's packaged human mapping
connects Entrez IDs with gene symbols.

### Environment

The Python installation and packages used by a project. A virtual environment
keeps one project's packages separate from other projects.

### Evidence code

A code in a Gene Ontology GAF file describing the basis of an annotation. IEA
is one evidence-code category.

### Expression matrix

A table with genes in rows and samples in columns. The cells contain numeric
gene measurements.

## F

### False discovery rate

The expected proportion of false discoveries among selected results. It is
often shortened to **FDR**. The q-value is the adjusted value used to control
this rate.

### Fisher meta-method

One option for combining directional p-values across prepared comparison
columns. Select it with `meta_method="fisher"`.

### Fold change

A measure of change between sample and reference values.

### Function

A named piece of Python code that performs a task. `gage`, `read_matrix`, and
`load_gmt` are functions.

## G

### GAF

Gene Association File. A tab-separated Gene Ontology annotation format that
connects genes to GO terms and records evidence and domain information.

### GAGE

Generally Applicable Gene-set Enrichment. GAGE is the statistical method
implemented by PyGAGE.

### Gene

A unit of inherited biological information. A data table represents a gene
with an identifier.

### Gene ID

A label that identifies a gene, such as an Entrez ID, symbol, Ensembl ID, or
KO ID.

### Gene set

A named list of related gene identifiers. A set may describe a pathway, GO
term, complex, process, location, or research-defined group.

### `GeneSetCollection`

A PyGAGE object that stores gene sets together with metadata such as source,
release, retrieval date, set count, and checksum.

### Gene symbol

A short human-readable gene label such as `TP53`, `BRCA1`, or `EGFR`.

### Gene Ontology

A structured vocabulary for Biological Process, Molecular Function, and
Cellular Component annotations. Its abbreviation is **GO**.

### Genome

The complete genetic material of an organism. Organism-specific KEGG pathways
are available when KEGG has a genome entry for the organism.

### GMT

Gene Matrix Transposed. A tab-separated gene-set format in which each line
contains a set name, description, and member genes.

### GO term

One concept in Gene Ontology, identified by a label such as `GO:0008150`.

### Greater

The PyGAGE result direction for gene sets tending toward higher or more
positive input measurements.

### `.gz`

A compressed-file ending. Polars and PyGAGE loaders can read supported
compressed tables and collections directly.

## H

### `.h5ad`

The standard file extension for a saved AnnData object.

### Heatmap

A grid whose cell colors represent numeric values. PyGAGE can draw enrichment
heatmaps across conditions and expression heatmaps for selected genes.

### HN

Head-and-neck tissue in the packaged GSE16873 demonstration dataset.

### HPC

High-performance computing. Shared computing systems often require explicit
thread and worker limits.

## I

### ID mapping

A table or operation connecting one identifier system to another, such as
Entrez IDs to gene symbols.

### IEA

Inferred from Electronic Annotation. A Gene Ontology evidence code. PyGAGE can
include it or omit it while building GO gene sets.

### Import

A Python statement that makes a package, class, or function available:

```python
from pygage import gage
```

### Input

Data supplied to an analysis. PyGAGE needs gene measurements and gene sets.

### `input_logged`

A preparation setting describing whether expression values are already on a
log scale. With `False`, PyGAGE applies `log2(x + 1)` before calculating
changes.

## J

### JSON

JavaScript Object Notation. A structured text format used for saved gene-set
dictionaries and metadata. Its usual extension is `.json`.

### JupyterLab

A browser-based environment for working with notebooks, files, terminals,
tables, and figures.

### Jupyter notebook

An `.ipynb` document containing code cells, Markdown cells, and saved output.

## K

### KEGG

Kyoto Encyclopedia of Genes and Genomes. PyGAGE retrieves KEGG pathway,
module, organism, and Orthology gene-set information through KEGG's REST
service.

### KEGG module

A smaller functional unit defined by KEGG. PyGAGE can retrieve
organism-specific modules or KO-based reference modules.

### KEGG organism code

A short code identifying a species in KEGG. Examples include `hsa` for human
and `mmu` for mouse.

### KEGG Orthology

A species-independent system grouping genes with equivalent functional roles.
Its abbreviation is **KO**.

### Kernel

The Python process running a Jupyter notebook. It stores variables created by
executed cells until it is restarted or shut down.

### KO ID

A KEGG Orthology identifier such as `K00844`.

### KS test

A rank-based Kolmogorov-Smirnov gene-set test selected with
`test_method="ks-test"`.

## L

### Leading edge

Member genes contributing strongly to a gene-set result. PyGAGE can add up to
25 identifiers in `leading_edge` when `leading_edge=True`.

### Less

The PyGAGE result direction for gene sets tending toward lower or more
negative input measurements.

### limma

A differential-expression tool whose result tables can be read with
`read_de_table`.

### Log2 fold change

A base-2 measure of change. Positive values represent increases relative to
the chosen reference; negative values represent decreases.

## M

### Mapping file

A table connecting identifiers. PyGAGE's `GeneIDConverter` accepts a table with
an ID column followed by a symbol column.

### Matched gene

A gene identifier present in both the measurement table and one gene set.
Only matched members contribute to that set's test and `set_size`.

### Measurement

A number associated with a gene, such as expression, log2 fold change, test
statistic, abundance change, or ranked score.

### Meta-method

The method that combines p-values across prepared comparison columns. PyGAGE
offers Stouffer and Fisher methods.

### Metadata

Information describing data rather than the measurement values themselves.
Examples include source, release, retrieval date, species, and checksum.

### Molecular Function

One Gene Ontology domain describing an activity performed by a gene product.
Its abbreviation is **MF**.

### MSigDB

Molecular Signatures Database. Its collections are commonly distributed as GMT
files and can be loaded by PyGAGE.

### Multiple testing

Testing many gene sets in one analysis. PyGAGE uses adjustment to report
q-values alongside p-values.

## N

### `n_jobs`

The number of workers used across gene sets in the Python analysis API. `1`
uses one worker, a positive integer requests that many workers, and `-1`
allows all available cores.

### NaN

Not a Number. A special numeric value used for a missing or undefined
measurement. PyGAGE's core calculations use NaN-aware operations.

### Node

A machine or computer allocated by a shared or HPC system.

### Null model

A model describing results expected without the enrichment pattern being
tested. A permutation analysis builds an empirical null by rearranging labels.

## O

### OBO

Open Biomedical Ontologies format. `go-basic.obo` supplies GO term names and
parent relationships used for optional annotation propagation.

### Offline analysis

An analysis using files already stored locally. The packaged GSE16873 workflow
on page 26 runs offline after PyGAGE is installed.

### One-call workflow

The high-level `gage()` route that prepares supported input when needed, runs
the analysis, and normally returns one tidy table.

### Organism

A species represented in a biological database.

### Output

A table, figure, metadata record, or other file created by an analysis.

## P

### Paired comparison

A design in which each sample column is matched to a particular reference
column, such as measurements from the same participant.

### pandas

A Python table library. PyGAGE accepts pandas DataFrames and converts them at
the input boundary.

### Parameter

A named function setting such as `test_method`, `set_size_range`, or
`random_state`.

### Pathway

A named group of biological interactions or functions. In enrichment
analysis, a pathway is represented as a gene set.

### Permutation

A rearrangement used to generate an empirical reference distribution.
`permutations` controls how many rearrangements PyGAGE performs.

### Polars

The primary table library used by PyGAGE. A Polars DataFrame is a table with
named columns.

### Prepared data

A table whose numeric columns already contain gene-level changes or
statistics ready for the gene-set test.

### Pre-ranked data

A table or mapping containing one gene identifier and one numeric score per
gene.

### Provenance

A record of where data came from and how it was created. Useful provenance
includes source, release, retrieval date, checksum, preprocessing, and
software version.

### p-value

A measure of statistical evidence under the test's null model. Smaller values
provide stronger evidence, but many tested gene sets also require
multiple-testing adjustment.

### `p_geomean`

The geometric mean of directional p-values across prepared comparison columns.

### `p_perm`

The optional permutation p-value reported when `permutations` is greater than
zero.

## Q

### q-value

The multiple-testing-adjusted value reported in `q_val`. Standard PyGAGE uses
Benjamini-Hochberg adjustment.

## R

### Random seed

A number controlling a reproducible sequence of random operations.
`random_state` sets the seed for PyGAGE permutation work.

### Ranked score

One numeric value per gene used to order genes, such as a test statistic or
log2 fold change.

### Reactome

A curated pathway database. PyGAGE loads Reactome GMT files and
NCBI2Reactome mapping files.

### Reference

The baseline condition against which sample measurements are compared.

### Release

A named or dated database or software version. Recording the release helps
another researcher identify the same resource.

### Reproducibility

The ability to recreate an analysis from its data, code, versions, settings,
and recorded decisions.

### Result table

A table containing one row per tested gene set and direction, with statistics
such as `set_size`, `p_val`, and `q_val`.

### Row

A horizontal record in a table. In a gene measurement table, one row normally
represents one gene.

## S

### Sample

One measured biological specimen, participant, condition, cell group, or other
experimental unit represented by a numeric column.

### Score

A numeric value used for ordering or analysis. The biological meaning depends
on how the score was calculated.

### Script

A plain-text `.py` file containing Python code that can be run again.

### Set-size range

The minimum and maximum number of matched genes allowed for a tested set.
PyGAGE's standard range is 10 through 500.

### `set_size`

The number of gene-set members found in the measured input.

### Species

An organism. Database retrieval and identifier mapping often require a species
or organism code.

### Staged workflow

The explicit route using `GAGEPreparation` followed by `GAGEAnalysis`. It is
helpful when the prepared table or advanced settings need to be inspected.

### Statistic

A number summarizing a pattern in the data. PyGAGE reports the mean
gene-set statistic as `stat_mean`.

### Stouffer meta-method

PyGAGE's standard method for combining directional p-values across prepared
comparison columns. Select it with `meta_method="stouffer"`.

### Symbol

See [Gene symbol](#gene-symbol).

## T

### t-test

The standard PyGAGE gene-set statistic, selected with
`test_method="t-test"`.

### Terminal

A text interface for entering commands on macOS and Linux. Windows PowerShell
serves the same role in this guide.

### Thread

A unit of computational work. Thread limits help PyGAGE, Polars, and numeric
libraries share a computer appropriately.

### Tidy result

One result table containing both directions and a `direction` column. The
high-level `gage()` function returns this form by default.

### TSV

Tab-separated values. A plain-text table format whose columns are separated by
tabs. Its usual extension is `.tsv`.

## U

### Unpaired comparison

A design in which sample and reference columns are not one-to-one matches.
PyGAGE prepares every sample-versus-reference combination.

### Universe

The full collection of measured genes considered by an analysis. It is also
called the measured-gene background.

## V

### Variable

A name attached to a Python object:

```python
result = gage(prepared, gene_sets, prepared=True)
```

Here, `result` is a variable containing the returned table.

### Vector

An ordered one-dimensional collection of values. A pre-ranked vector connects
one score to each gene.

### Virtual environment

A private Python environment for one project. This guide names it `.venv`.

## W

### Worker

One execution unit used to process gene sets in parallel. `n_jobs` controls
the requested worker count.

## Z

### z-test

A PAGE-style gene-set statistic offered by PyGAGE, selected with
`test_method="z-test"`.

[<- Previous: Recipe book](28-recipe-book.md) | [Home](index.md) | [Next: Complete Python API ->](30-api-reference.md)
