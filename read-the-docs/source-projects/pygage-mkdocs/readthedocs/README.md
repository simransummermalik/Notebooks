# PyGAGE Read the Docs project

This folder contains the source for a beginner-to-advanced PyGAGE
documentation website. The first pages assume no coding or gene-set enrichment
experience. Later pages introduce each optional input, gene-set source,
statistical setting, plot, command, and public Python interface.

## Folder map

```text
readthedocs/
├── docs/              # Markdown pages shown on the website
├── mkdocs.yml         # Website title, theme, and chapter menu
└── requirements.txt   # Packages used to build the website
```

The project-level `.readthedocs.yaml` file tells Read the Docs to build the
website from this folder.

## Preview the website

Run these commands from the `pygage-mkdocs` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r readthedocs/requirements.txt
mkdocs serve --config-file readthedocs/mkdocs.yml
```

Open `http://127.0.0.1:8000` in a browser.

## Check the website

```bash
mkdocs build --strict --config-file readthedocs/mkdocs.yml
```

A successful strict build confirms that the navigation, Markdown files, and
internal links are ready for Read the Docs.
