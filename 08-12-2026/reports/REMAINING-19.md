# Nineteen August 10 findings still reproduced in Pathview Plus 3.1.0

I rewrote these checks only where necessary to use the v3 interface. In each row, the old problem is shown next to what the current check produced. A row can stay here after a partial improvement; for example, XML response validation improved for `PV-BUG-057`, but mocked HTML was still accepted as a PNG.

## Five original P1 findings

P1 is the original August 10 triage label, not a newly calculated v3 severity score.

| ID | August 10 problem | What the v3.1.0 recheck produced |
|---|---|---|
| `PV-BUG-006` | map_null=False does not remove unmapped rows when a data table exists | With map_null=False and one matched gene, plot_data_gene still had 27 rows while only 1 row carried a value. |
| `PV-BUG-034` | bbox_inches='tight' crops/rescales native output instead of preserving KEGG pixels | A 120x100 native background saved as a 792x664 output with title, key, and signature disabled at dpi=100. |
| `PV-BUG-038` | graph/PDF renderer uses only the first experiment color | Graph rendering reduced two colors per node to one node_color entry per node. |
| `PV-BUG-074` | Reactome SBGN file exporter route is coded as /exporter/sbgn/{id}.sbgn instead of /exporter/event/{id}.sbgn | REACTOME_SBGN is still https://reactome.org/ContentService/exporter/sbgn and constructs .../sbgn/{id}.sbgn. |
| `PV-BUG-075` | _add_symbol_labels joins a SYMBOL column but never replaces the rendered label | _symbol_labels returned an empty label map for a gene whose existing label was the Entrez text '7157'. |

## Fourteen original P2/P3 findings

These rows cover validation boundaries, parser information loss, and integration details rather than only visible crashes.

| ID | August 10 problem | What the v3.1.0 recheck produced |
|---|---|---|
| `PV-BUG-003` | Python API does not validate output_format; unknown values become PDF | The Python API accepted output_format='jpg' and output_format='PNG' even though the documented choices are png, pdf, and svg. Empty input failed as FileNotFoundError and 'banana' failed in Matplotlib, not in pathview's API validation. |
| `PV-BUG-007` | min_nnodes counts pathway layout nodes, not nodes matched by input data | One completely unmatched input ID with min_nnodes=1 returned a truthy result with 64 layout nodes and plot_data_gene=None. |
| `PV-BUG-010` | pathway prefixes that conflict with species are concatenated, not rejected | pathview('mmu00020', species='hsa') looked for hsammu00020.xml and raised PathwayNotFoundError rather than rejecting the conflicting prefix. |
| `PV-BUG-017` | negative experiment count is silently accepted | sim_mol_data('cpd', n_exp=-1) returned columns ['compound', 'exp1']. |
| `PV-BUG-020` | duplicate KGML entry IDs silently overwrite earlier entries | Two KGML entries with id='1' parsed successfully and the second entry overwrote the first. |
| `PV-BUG-021` | line graphics coords are ignored and replaced with zero/default geometry | A KGML line with coords='10,20,30,40' parsed with x=None, y=None, width=46, height=17. |
| `PV-BUG-027` | Bezier control &lt;point&gt; children inside SBGN &lt;next&gt; are discarded | Nested SBGN control points (20,20) and (25,20) were omitted; only start, next, and end coordinates remained. |
| `PV-BUG-049` | unknown routing mode silently falls back to straight | route_edge_spline(..., routing_mode='banana') returned a finite (30,2) curve rather than rejecting the mode. |
| `PV-BUG-056` | invalid KEGG file types fail with internal KeyError instead of validation error | download_kegg(..., file_type=['banana']) raised KeyError('banana'). |
| `PV-BUG-057` | KEGG downloader trusts any HTTP 200 body without format/content validation | A mocked HTTP 200 HTML body for a PNG was written to hsa00020.png and reported as succeed. XML now has a content check, so this is a partial fix only. |
| `PV-BUG-061` | KEGG chemical conversion uses alias 'cpd' where API specifies 'compound' | The generated KEGG conversion URL still used /conv/cpd/ rather than /conv/compound/. |
| `PV-BUG-062` | already-prefixed compound IDs receive a duplicate source prefix | An already-prefixed input produced /conv/cpd/pubchem:pubchem:123. |
| `PV-BUG-064` | database detection is unexpectedly case-sensitive | Uppercase Reactome/PANTHER IDs resolved, while lowercase forms returned null. |
| `PV-BUG-069` | all-transparent SVG nodes are forcibly recolored gray | render_node_svg replaced a transparent fill with the theme's unmapped color. |
