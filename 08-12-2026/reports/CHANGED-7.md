# Seven findings reclassified because v3 replaced the relevant interface

These seven are not part of the 60 fixed or the 19 still reproducible rows. In each case, v3.1.0 removed or replaced the argument, command, or dispatch path used by the old reproducer. I recorded what v3 uses instead without treating the replacement itself as proof that it is correct.

| ID | August 10 problem | What v3.1.0 uses instead / fair follow-up |
|---|---|---|
| `PV-BUG-005` | a partial color config replaces defaults instead of merging per molecule type | v3 uses separate `ColorScale`, `gene_color`, and `cpd_color` settings. A fair follow-up is to test partial settings through the new scale API. |
| `PV-BUG-016` | entrez_gnodes is unused and species prefixes are always stripped | The `entrez_gnodes` switch was removed; identifiers are normalized while KGML is parsed and mapping uses `kegg_names`. A fair follow-up is to test prefixed and unprefixed KEGG IDs through the new mapper. |
| `PV-BUG-018` | decimal strings are parsed as hexadecimal numbers | String-valued columns are excluded from numeric color mapping instead of being interpreted as hexadecimal values. A fair follow-up is to decide whether numeric strings should be rejected or explicitly coerced. |
| `PV-BUG-047` | obstacles argument is not consulted by routing implementation | Obstacle handling is now the documented `routing_mode='avoid'` path. A fair follow-up is to test that mode with a supplied obstacle. |
| `PV-BUG-067` | SVG output unnecessarily requires/downloads a KEGG PNG when kegg_native=True | The `render_mode` argument now selects native, vector, graph, or SVG behavior. A fair follow-up is to run SVG mode with KGML present and no PNG. |
| `PV-BUG-077` | --simulate branch silently ignores a supplied --cpd-data file | The old CLI `--simulate` branch was removed; simulation remains available through Python data-generation functions. There is no like-for-like CLI call to recheck. |
| `PV-FEATURE-007` | non-KEGG database detection/download/parsing is not wired through pathview() | Non-KEGG work now uses `sbgnview()` and `sbgnview_batch()` rather than dispatching through `pathview()`. A fair follow-up is to test download, parse, map, and render through that entry point. |
