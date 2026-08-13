# Read the Docs work

Everything related to documentation websites is kept here.

## Folder map

```text
read-the-docs/
├── source-projects/
│   ├── pathview-plus/          Pathview Plus MkDocs project
│   └── pygage-mkdocs/          Separate beginner PyGAGE MkDocs project
├── upstream-handoff/
│   └── pygage-sphinx/          Beginner addition for the official Sphinx docs
├── previews/
│   ├── pygage-sphinx-original/ Original generated PyGAGE website
│   └── pygage-sphinx-updated/  Generated website with the beginner addition
└── archives/
    └── pygage/2026-07-29/      Original, preview, and handoff packages
```

## What to edit

- Edit [`source-projects/pathview-plus/`](source-projects/pathview-plus/) for
  the standalone Pathview Plus Read the Docs project.
- Edit [`source-projects/pygage-mkdocs/`](source-projects/pygage-mkdocs/) for
  the separate beginner-first PyGAGE MkDocs project.
- Use [`upstream-handoff/pygage-sphinx/`](upstream-handoff/pygage-sphinx/) when
  reviewing the smaller change intended for the existing official PyGAGE
  Sphinx documentation.

The folders under `previews/` are generated websites for viewing. The files
under `archives/` are saved packages and should not be edited directly.
