# Cite, reproduce, and support your work

*Page 24 of 24*

Use this page when you are preparing a report, presentation, manuscript,
shared analysis, contribution, or project question.

The goal is to leave a clear record of what data were mapped, which pathway was
used, and how the finished figure was made.

## Record the software version

The examples in this guide use **Pathview Plus 2.0.2**.

Check the installed package record with:

```bash
python -m pip show pathview-plus
```

Also record the Python version:

```bash
python --version
```

For a complete environment record:

```bash
python -m pip freeze > requirements-lock.txt
```

Keep `requirements-lock.txt` with the analysis script and input table. It lists
the exact installed package versions used by that environment.

## Find the official project and package

- Source repository:
  [raw-lab/pathview-plus](https://github.com/raw-lab/pathview-plus)
- Python package:
  [pathview-plus on PyPI](https://pypi.org/project/pathview-plus/)

Use the project's official paper citation when it is released. Check the
repository, package page, and published paper for the final author order,
title, journal information, and DOI. Do not create or guess a DOI.

Until the official citation is available, preserve a software record with:

- software name: Pathview Plus;
- version: `2.0.2`;
- repository URL;
- date accessed; and
- the exact analysis script.

Also follow the citation and use guidance for the pathway database and any
identifier or annotation resources used in the analysis.

## Figure-caption template

Copy this template and replace every bracketed item:

```text
Pathview Plus 2.0.2 visualization of the [species or KO reference]
[pathway name] pathway ([pathway ID]). [Data type] values were mapped
using [identifier type]. Colors represent [measurement, units, and
comparison], from [low color and limit] through [middle color/value] to
[high color and limit]. [Conditions or time points] are shown in
[left-to-right order]. The figure was generated on [date] with
[script filename] from [input filename]. Pathway source: [database].
```

Example details that belong in a caption include:

- whether the values are log2 fold change, abundance difference, expression,
  score, or another measurement;
- whether the pathway is species-specific or a `ko` reference pathway;
- the order of multiple conditions;
- what highlighted borders and lines mean; and
- whether the output is PNG, SVG, or PDF.

## Reproducibility checklist

Before sharing a final figure, save:

- [ ] Pathview Plus version `2.0.2`;
- [ ] Python version and package environment;
- [ ] pathway database, pathway ID, pathway name, and species code;
- [ ] date the pathway file was obtained;
- [ ] original input table;
- [ ] identifier type used in the first column;
- [ ] description, units, and comparison for every numeric column;
- [ ] any filtering, centering, aggregation, or ID-conversion steps;
- [ ] the `node_sum` rule when several rows can map to one node;
- [ ] low, middle, and high colors;
- [ ] color limits, bins, and color-key choice;
- [ ] output format and renderer choice;
- [ ] complete Python script or notebook;
- [ ] finished figure and its caption; and
- [ ] citations required by the software, pathway source, and input resources.

A clear project folder might look like:

```text
my-pathview-project/
├── data/
│   └── gene_results.tsv
├── scripts/
│   ├── pathview_setup.py
│   └── make_pathway.py
├── pathview_output/
│   └── hsa04151.final_figure.svg
├── requirements-lock.txt
└── figure_caption.txt
```

## Choose a workflow for your data source

Pathview Plus colors pathway nodes with numerical values. Use this table to
choose the preparation page that matches your source data.

| Data source | Prepare for Pathview Plus | Continue with |
| --- | --- | --- |
| transcriptomics | keep gene IDs and one or more gene-level measurements | [one condition](06-one-gene-condition.md), [several conditions](07-multiple-gene-conditions.md), or [ID conversion](16-identifier-conversion.md) |
| proteomics | connect protein accessions to a supported gene identifier and keep protein- or gene-level values | [prepare data](04-prepare-your-data.md), [ID conversion](16-identifier-conversion.md), then [gene mapping](06-one-gene-condition.md) |
| genetic variants | summarize the chosen variant result at the gene level and document the summary rule | [prepare data](04-prepare-your-data.md), then [gene mapping](06-one-gene-condition.md) |
| metabolomics | keep compound IDs and compound-level abundance or change values | [compound and multi-omics mapping](09-compounds-and-multiomics.md) and [ID conversion](16-identifier-conversion.md) |
| pathway enrichment | use enriched pathway IDs to choose diagrams, then use gene, KO, or compound measurements to color their nodes | [choose a pathway](05-choose-a-pathway.md), [gene mapping](06-one-gene-condition.md), [KO mapping](08-kegg-orthology.md), or [compound mapping](09-compounds-and-multiomics.md) |
| microbiome or metagenomics | summarize annotated functions as KO-level values; keep one column per comparison when needed | [KO mapping](08-kegg-orthology.md) and [several conditions](07-multiple-gene-conditions.md) |

For multi-omics work, prepare the gene and compound tables separately, record
the units of each, and then use
[the combined workflow](09-compounds-and-multiomics.md#part-b-map-genes-and-compounds-together).

## Ask a clear project question

Start by searching this guide and the
[project repository](https://github.com/raw-lab/pathview-plus). If a software
question still needs discussion, prepare a small, reproducible example.

Include:

1. a short title that states the task;
2. Pathview Plus, Python, and operating-system versions;
3. the pathway ID, species code, and identifier type;
4. a minimal script that can be copied and run;
5. a tiny synthetic or public input table;
6. what you expected to see;
7. what you observed; and
8. the relevant console text or a small screenshot.

Keep confidential, clinical, participant, and unpublished project data out of
public reports. Replace them with a tiny synthetic example that preserves the
same table structure.

Project discussions and reports can be opened through the repository's
[GitHub Issues page](https://github.com/raw-lab/pathview-plus/issues).

## Suggest a feature professionally

A useful feature request explains:

- the scientific or documentation goal;
- who would use it;
- the proposed input and output;
- one small example;
- how it fits the current workflow; and
- whether you are willing to help test or document it.

For example:

```text
Goal: Let a new user upload a two-column gene table and create a pathway
image through a simple form.

Input: A table, species code, pathway ID, identifier type, and output format.

Output: A downloadable pathway image plus a record of the selected settings.

I can help test the beginner workflow and write the documentation example.
```

This format makes the scientific need and the proposed user experience easy
for the team to evaluate.

## Contribute documentation or code

Before proposing a change:

1. read the repository contribution guidance;
2. keep one contribution focused on one clear goal;
3. use a descriptive branch and commit message;
4. explain what changed and how it was checked;
5. include a small example for a new public feature;
6. update the matching documentation page; and
7. respond to review comments with the new commit or a concise explanation.

Documentation examples should use small teaching data, exact filenames, pinned
versions, and links to the next relevant page. That keeps the guide friendly
to first-time users and useful to experienced researchers.

## Final handoff checklist

You are ready to share the work when another person can:

1. identify the input data and its units;
2. find the exact pathway and species;
3. recreate the software environment;
4. run the saved script;
5. obtain the same output format and colors; and
6. understand the figure from its caption.

[<- Previous: Complete API reference](23-api-reference.md) | [Home](index.md)
