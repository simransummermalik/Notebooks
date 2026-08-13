# PyGAGE documentation update: everything changed

## Baseline used

This update is based on the official `raw-lab/pygage` source at:

```text
PyGAGE version: 1.2.1
Commit: 486e0b800778ec03fe03764aa9dccbe904cfd70b
```

The supplied website now stored in
`../../previews/pygage-sphinx-original/` was verified as a Sphinx build of that
official source.

## Upstream-ready documentation changes

Only four source-level changes are proposed for the official PyGAGE
documentation:

### 1. Added `doc/source/beginner/index.md`

This new beginner landing page adds:

- a plain-language explanation of PyGAGE;
- definitions of gene, gene set, measurement, enrichment, `greater`, and
  `less`;
- an explanation that measurement IDs and gene-set IDs must match;
- a routing table for raw expression, prepared changes, differential-expression
  tables, pre-ranked input, pandas, AnnData, and the supported gene-set sources;
- a checklist of decisions to record before a real analysis; and
- links into the existing installation, quickstart, inputs, gene-set, and
  results pages.

### 2. Added `doc/source/beginner/first-analysis.md`

This new step-by-step tutorial adds:

- a complete twelve-gene teaching dataset;
- three small teaching gene sets;
- one copyable `gage()` script;
- instructions for running the script;
- CSV export to `all_results.csv` and `significant_results.csv`;
- the verified expected `Growth pathway`/`greater` and
  `Stress pathway`/`less` results;
- an explanation of `prepared=True`;
- an explanation of the teaching set-size range;
- a plain-language explanation of direction, matched set size, and q-values;
  and
- links to the existing real-data quickstart, results guide, and method page.

### 3. Added `doc/source/beginner/prepare-data.md`

This new preparation tutorial adds:

- the expected genes-by-samples table shape;
- a reminder to retain gene identifiers as text;
- the zero-based sample-column numbering rule;
- an example that prints the column positions before analysis;
- a comparison table for `paired`, `unpaired`, `as.group`, and `1ongroup`;
- a complete `GAGEPreparation.prepare_expression()` example;
- explanations of `input_logged` and `same_dir`;
- a reminder to complete the study's planned normalization before preparation;
- an identifier-overlap check;
- human gene-symbol to Entrez-ID conversion with `GeneIDConverter`;
- preservation and review of the original symbols before conversion;
- handling of unmapped identifiers;
- Entrez-ID to symbol conversion; and
- guidance for using a species-appropriate mapping.

### 4. Updated `doc/source/index.rst`

One hidden six-line toctree block was added:

```rst
.. toctree::
   :hidden:
   :caption: Beginner guide

   beginner/index
```

This adds the new beginner section to the existing Furo sidebar. No existing
navigation entry was removed or renamed.

## Styling and theme preservation

The styling is the same as the supplied website.

The following are byte-for-byte unchanged:

- `doc/source/conf.py`;
- `doc/source/_static/custom.css`;
- `doc/source/_static/logo.svg`;
- `doc/source/_static/favicon.svg`;
- every generated file under `_static/`; and
- every generated file under `_sphinx_design_static/`.

The updated build uses the same identified website versions:

```text
Sphinx 9.1.0
Furo 2025.12.19
sphinx-design 0.7.0
MyST Parser 5.1.0
sphinx-copybutton 0.5.2
```

The colors, typography, logo, dark mode, code blocks, copy buttons, responsive
layout, and sidebar behavior therefore remain consistent with the supplied
site.

## Existing content preserved

All pre-existing files under `doc/source/` are byte-for-byte unchanged except
for the six-line navigation addition in `index.rst`.

In particular, this update does not rewrite or duplicate the existing:

- installation page;
- real-data quickstart;
- method explanation;
- input and gene-set reference pages;
- results and visualization pages;
- four newer PyGAGE charts;
- CLI documentation;
- validation and performance pages;
- API reference; or
- changelog.

The copied PyGAGE 1.2.1 source under `src/pygage/` is included so the review
copy can build the API documentation. It was not modified.

## Generated website changes

Sphinx generated three new HTML pages:

```text
beginner/index.html
beginner/first-analysis.html
beginner/prepare-data.html
```

It also regenerated the normal site navigation, previous/next links, search
index, object inventory, module pages, and sidebar markup so the new pages are
discoverable. These generated files were created by Sphinx and were not edited
by hand.

## Review and validation files added

The review package also contains:

- `DOCS-HANDOFF.md` — how to build and hand the source changes upstream;
- `SOURCE-INTEGRITY.md` — the official baseline and preservation boundary;
- `BUILD-REPORT.md` — the completed build and validation record;
- `validation/validate_beginner_examples.py` — executes the documented
  beginner examples; and
- `validation/check_html_links.py` — checks local HTML files and fragments.

These files support review and are not proposed additions to the official
PyGAGE documentation.

## Checks completed

- Strict Sphinx build with warnings treated as errors: passed.
- Sphinx external-link check: passed.
- Internal file and fragment check across 31 HTML pages: passed.
- Twelve-gene tutorial execution: passed.
- Paired expression preparation: passed.
- Human symbol-to-Entrez conversion: passed.
- Entrez-to-symbol conversion: passed.
- Existing documentation source preservation comparison: passed.
- Theme and generated static-asset comparison: passed.

## Original files and publication status

The original archive under `../../archives/pygage/2026-07-29/baseline/` and the
extracted website under `../../previews/pygage-sphinx-original/` remain
separate and unchanged.

Original archive SHA-256:

```text
34a94124ea11771726c223d3b20ab2f2a6488e2be32ac276ecbe51ca1017e824
```

This update is local. It has not been committed, pushed, merged into
`raw-lab/pygage`, or published on Read the Docs.

## ZIP contents

The complete ZIP contains:

```text
PYGAGE-DOCS-CHANGES.md       complete change list
pygage-docs-update/          Sphinx source, support files, and built preview
pygage_docs_html_updated/    standalone updated HTML preview
```
