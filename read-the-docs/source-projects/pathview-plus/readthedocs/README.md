# Pathview Plus Read the Docs project

This folder contains the source for the beginner-to-advanced Pathview Plus
documentation website. Pages 1–14 form the simple KEGG learning route. Pages
15–24 explain additional output, identifier, command-line, database,
rendering, and reporting tools.

## Folder map

```text
readthedocs/
├── docs/              # Markdown pages shown on the website
├── mkdocs.yml         # Website title, theme, and chapter menu
└── requirements.txt   # Packages used to build the website
```

The repository-level `.readthedocs.yaml` file tells Read the Docs to build the
site from this folder.

## Edit the guide

- Edit `docs/index.md` to change the website homepage.
- Edit a numbered Markdown file to change a guide page.
- Edit the `nav` section of `mkdocs.yml` when adding, removing, or renaming a
  page.
- Keep each page's Previous, Home, and Next links connected.

## Preview the website

Run these commands from the repository's main folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r readthedocs/requirements.txt
mkdocs serve --config-file readthedocs/mkdocs.yml
```

Open `http://127.0.0.1:8000` in a web browser. The preview updates after a
Markdown file is saved.

## Check the website before publishing

Run:

```bash
mkdocs build --strict --config-file readthedocs/mkdocs.yml
```

A successful build confirms that the chapter menu, Markdown files, and
internal links are ready for Read the Docs.
