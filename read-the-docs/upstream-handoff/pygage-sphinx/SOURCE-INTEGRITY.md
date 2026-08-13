# Source integrity record

## Official baseline

- Repository: `raw-lab/pygage`
- Commit: `486e0b800778ec03fe03764aa9dccbe904cfd70b`
- Version documented: PyGAGE 1.2.1
- Editable Sphinx source: `doc/source/`

The received archive is preserved separately at
`../../archives/pygage/2026-07-29/baseline/pygage-docs-site.tar`.
Its SHA-256 checksum is:

```text
34a94124ea11771726c223d3b20ab2f2a6488e2be32ac276ecbe51ca1017e824
```

The separately extracted `../../previews/pygage-sphinx-original/` folder and
the original archive are not edited by this documentation update.

## Source and generated files

Edit only source files under `doc/source/`. The following are build products,
not documentation source:

- `*.html`
- `.doctrees/`
- `_modules/`
- generated `_static/` files
- `objects.inv`
- `searchindex.js`

Generated files should be recreated with Sphinx in a separate build directory,
not changed by hand.

## Approved change boundary

The upstream patch should contain only:

1. new beginner pages under `doc/source/beginner/`; and
2. one deliberate navigation addition in `doc/source/index.rst`.

`DOCS-HANDOFF.md` and this file describe the review copy and are not intended
for upstream. The root `README.md` remains the untouched official upstream file.

## Review checklist

Before handing the update to the maintainers:

1. Confirm the source diff contains only the approved files above.
2. Run a clean local build:

   ```bash
   python -m sphinx -b html -E -a \
     -D exclude_patterns=readme.md,_static/readme.md \
     -d doc/build/doctrees \
     doc/source doc/build/html
   ```

3. Run the strict build in an internet-connected environment:

   ```bash
   python -m sphinx -b html -E -a -W --keep-going \
     -D exclude_patterns=readme.md,_static/readme.md \
     -d doc/build/doctrees \
     doc/source doc/build/html
   ```

4. Check the landing page, sidebar, beginner-page order, internal links, code
   blocks, mobile layout, and search.
5. Run any documented Python examples independently.
6. Recheck the original archive if needed:

   ```bash
   shasum -a 256 ../../archives/pygage/2026-07-29/baseline/pygage-docs-site.tar
   ```

The local build is for review only. Nothing in this folder publishes a website.
