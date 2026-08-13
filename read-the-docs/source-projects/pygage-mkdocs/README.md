# PyGAGE: a step-by-step Markdown guide

This Read the Docs project teaches PyGAGE gene-set enrichment to readers who
have little or no coding experience.

The documentation is based on PyGAGE 1.2.1 from
[raw-lab/pygage](https://github.com/raw-lab/pygage), reviewed at source commit
`486e0b800778ec03fe03764aa9dccbe904cfd70b`. It begins with a complete toy
enrichment and gradually introduces real matrices, DE tables, pre-ranked data,
gene-set databases, statistics, plots, notebooks, CLI commands, and the full
Python API.

## Documentation website source

- [Website homepage](readthedocs/docs/index.md)
- [All numbered Markdown chapters](readthedocs/docs/)
- [MkDocs navigation](readthedocs/mkdocs.yml)
- [Read the Docs build configuration](.readthedocs.yaml)

## The whole idea

```text
gene measurements + groups of related genes -> ranked enriched gene sets
```

## Beginner route

1. [Before you begin](readthedocs/docs/01-before-you-begin.md)
2. [Install PyGAGE](readthedocs/docs/02-install.md)
3. [Run your first enrichment](readthedocs/docs/03-first-enrichment.md)
4. [Understand the first result](readthedocs/docs/04-understand-enrichment.md)
5. [Choose your input route](readthedocs/docs/05-choose-input.md)

## Complete chapter list

1. [Before you begin](readthedocs/docs/01-before-you-begin.md)
2. [Install PyGAGE](readthedocs/docs/02-install.md)
3. [Run your first enrichment](readthedocs/docs/03-first-enrichment.md)
4. [Understand the first result](readthedocs/docs/04-understand-enrichment.md)
5. [Choose your input route](readthedocs/docs/05-choose-input.md)
6. [Understand an expression matrix](readthedocs/docs/06-expression-matrix.md)
7. [Choose reference and sample columns](readthedocs/docs/07-reference-and-sample.md)
8. [Read and prepare the matrix](readthedocs/docs/08-prepare-expression.md)
9. [Understand gene sets](readthedocs/docs/09-gene-sets.md)
10. [Run the one-call workflow](readthedocs/docs/10-one-call-gage.md)
11. [Run the staged workflow](readthedocs/docs/11-staged-analysis.md)
12. [Use a differential-expression table](readthedocs/docs/12-de-tables.md)
13. [Use pre-ranked data](readthedocs/docs/13-preranked.md)
14. [Use pandas or AnnData](readthedocs/docs/14-pandas-anndata.md)
15. [Download KEGG gene sets](readthedocs/docs/15-kegg.md)
16. [Use KEGG Orthology data](readthedocs/docs/16-kegg-orthology.md)
17. [Build Gene Ontology sets](readthedocs/docs/17-gene-ontology.md)
18. [Use Reactome, MSigDB, GMT, and the cache](readthedocs/docs/18-other-gene-sets.md)
19. [Understand every result column](readthedocs/docs/19-results.md)
20. [Choose statistical settings](readthedocs/docs/20-statistical-settings.md)
21. [Use advanced analysis options](readthedocs/docs/21-advanced-options.md)
22. [Filter, group, compare, and export](readthedocs/docs/22-group-overlap.md)
23. [Make enrichment plots](readthedocs/docs/23-visualization.md)
24. [Use the command line](readthedocs/docs/24-command-line.md)
25. [Use a Jupyter notebook](readthedocs/docs/25-notebooks.md)
26. [Follow a real-data workflow](readthedocs/docs/26-real-dataset.md)
27. [Configure performance and threads](readthedocs/docs/27-performance.md)
28. [Recipe book](readthedocs/docs/28-recipe-book.md)
29. [Glossary](readthedocs/docs/29-glossary.md)
30. [Complete Python API](readthedocs/docs/30-api-reference.md)
31. [Cite, reproduce, and get support](readthedocs/docs/31-citation-and-support.md)

## Preview locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r readthedocs/requirements.txt
mkdocs serve --config-file readthedocs/mkdocs.yml
```

Then open `http://127.0.0.1:8000`.

## Publish on Read the Docs

Use this `pygage-mkdocs` folder as the top level of the PyGAGE documentation
repository. In other words, `.readthedocs.yaml`, `README.md`, and the
`readthedocs` folder should appear immediately when the GitHub repository is
opened.

Then:

1. commit and push the repository to GitHub;
2. import that GitHub repository in Read the Docs;
3. start the first build; and
4. open the build log and confirm that the configuration file and MkDocs
   project were detected.

Read the Docs will use:

- [`.readthedocs.yaml`](.readthedocs.yaml) for Python and build settings;
- [`readthedocs/requirements.txt`](readthedocs/requirements.txt) for pinned
  website packages; and
- [`readthedocs/mkdocs.yml`](readthedocs/mkdocs.yml) for the menu and theme.

Read the Docs documents the required repository-root placement in its
[configuration-file guide](https://docs.readthedocs.com/platform/stable/config-file/index.html).
