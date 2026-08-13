# Documentation build report

Date: 2026-07-29

## Result

The beginner addition builds successfully with the same Sphinx and Furo
versions identified in the supplied website.

Generated preview:

```text
doc/build/html/index.html
```

## Preservation check

Baseline:

```text
raw-lab/pygage
commit 486e0b800778ec03fe03764aa9dccbe904cfd70b
PyGAGE 1.2.1
```

A recursive comparison with that baseline found only:

```text
new:     doc/source/beginner/
changed: doc/source/index.rst
```

The `index.rst` difference is one six-line hidden toctree block. Every other
pre-existing documentation source file is unchanged.

The original supplied archive remains at:

```text
../../archives/pygage/2026-07-29/baseline/pygage-docs-site.tar
```

Its verified SHA-256 remains:

```text
34a94124ea11771726c223d3b20ab2f2a6488e2be32ac276ecbe51ca1017e824
```

## Checks completed

- Strict Sphinx HTML build: passed with warnings treated as errors.
- Sphinx external-link check: passed.
- Local HTML file and fragment check: 31 pages checked, 0 problems.
- Twelve-gene beginner analysis: passed.
- Paired expression preparation example: passed.
- Bundled human symbol-to-Entrez and Entrez-to-symbol examples: passed.
- Sidebar and search output: the three beginner pages are present.

Build environment:

```text
Sphinx 9.1.0
Furo 2025.12.19
sphinx-design 0.7.0
MyST Parser 5.1.0
sphinx-copybutton 0.5.2
```

The two placeholder files named `readme.md` are upstream repository notes
rather than documentation pages. The root placeholder was excluded at build
time, and the copied `_static/readme.md` placeholder was omitted from the
shareable HTML. No source file was removed or edited.

## Publication status

This is a local review build. It has not been pushed to the official PyGAGE
repository and has not been published on Read the Docs.
