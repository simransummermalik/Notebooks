# PyGAGE documentation update

This folder is a review and local-build copy of the official
[`raw-lab/pygage`](https://github.com/raw-lab/pygage) repository at commit
`486e0b800778ec03fe03764aa9dccbe904cfd70b`.

Its purpose is to add beginner-friendly documentation while preserving the
official PyGAGE documentation, code, styling, and generated website.

## What may change

The intended upstream change is limited to:

- new beginner documentation files under `doc/source/beginner/`; and
- one navigation entry in `doc/source/index.rst` that links to the beginner
  guide.

Existing PyGAGE pages should not be rewritten. See
[`SOURCE-INTEGRITY.md`](SOURCE-INTEGRITY.md) for the baseline and review rules.

## Build a local preview

From this folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[docs]"
python -m sphinx -b html -E -a \
  -D exclude_patterns=readme.md,_static/readme.md \
  -d doc/build/doctrees \
  doc/source doc/build/html
```

Open `doc/build/html/index.html` to review the local result. Building a preview
does not publish the documentation.

For a build that matches the supplied Furo site as closely as possible, use:

```bash
python -m pip install \
  "Sphinx==9.1.0" \
  "furo==2025.12.19" \
  "sphinx-design==0.7.0" \
  "myst-parser==5.1.0" \
  "sphinx-copybutton==0.5.2"
```

## Validate the update

The review copy includes two small checks:

```bash
python validation/validate_beginner_examples.py
python validation/check_html_links.py doc/build/html
```

For a strict external-link check:

```bash
python -m sphinx -b linkcheck -E -a -W --keep-going \
  -D exclude_patterns=readme.md,_static/readme.md \
  doc/source doc/build/linkcheck
```

## Upstream handoff

Copy the new folder and merge the six-line beginner toctree block into the
current upstream index:

```text
doc/source/beginner/
doc/source/index.rst
```

Do not copy `DOCS-HANDOFF.md`, `SOURCE-INTEGRITY.md`, `.venv/`,
`doc/build/`, or any generated HTML unless the maintainers specifically request
them.
