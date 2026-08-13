# Status of all 86 findings from the August 10 Pathview Plus audit

## Scope and how to read this table

This is a follow-up to the August 10 audit, not a new search for every possible Pathview Plus defect. It follows the same 86 unique finding IDs from commit `07aee813` (distribution `2.0.2`; runtime version string `2.0.0`) and checks their current equivalent at Pathview Plus `3.1.0`, commit `d4d45de`. Every ID received exactly one status.

The P1/P2-P3 labels are the original August 10 triage labels. P1 referred to a main workflow or advertised feature; P2/P3 covered lower-priority validation issues, API boundaries, and edge cases. The labels were not reassigned for v3.

| v3 status | Count | Definition used in this comparison |
|---|---:|---|
| Fixed | 60 | The old failure condition was absent in a current v3 test, adapted check, or source review. |
| Still reproducible | 19 | A current equivalent still showed the underlying behavior. |
| Changed interface/behavior | 7 | The old contract was replaced, so the old reproducer is neither a fair pass nor a fair fail. |
| **Total** | **86** | One row for each unique August 10 finding. |

Use this page as the index. Current reproduction details are in `REMAINING-19.md`; replacement contracts are in `CHANGED-7.md`; the 60 rows whose old condition was absent are in `FIXED-60.md`.

| ID | August 10 priority | August 10 description | Result at v3.1.0 |
|---|---|---|---|
| `PV-BUG-001` | P2/P3 | setup.py/distribution is 2.0.2 but pathview.__version__ is 2.0.0 | Fixed |
| `PV-BUG-002` | P2/P3 | --no-kegg-native with output_format='png' silently writes graph PDF | Fixed |
| `PV-BUG-003` | P2/P3 | Python API does not validate output_format; unknown values become PDF | Still reproducible |
| `PV-BUG-004` | P1 | cached files cannot bypass live species lookup | Fixed |
| `PV-BUG-005` | P2/P3 | a partial color config replaces defaults instead of merging per molecule type | Changed interface/behavior |
| `PV-BUG-006` | P1 | map_null=False does not remove unmapped rows when a data table exists | Still reproducible |
| `PV-BUG-007` | P2/P3 | min_nnodes counts pathway layout nodes, not nodes matched by input data | Still reproducible |
| `PV-BUG-008` | P1 | core returns dict while documented highlighting requires PathwayResult | Fixed |
| `PV-BUG-009` | P1 | mapped node table drops the exploded kegg_names identifier | Fixed |
| `PV-BUG-010` | P2/P3 | pathway prefixes that conflict with species are concatenated, not rejected | Still reproducible |
| `PV-BUG-011` | P2/P3 | empty KGML produces a schema-less frame and core crashes before graceful skip | Fixed |
| `PV-BUG-012` | P1 | group aggregation UDF receives scalar elements under current Polars | Fixed |
| `PV-BUG-013` | P2/P3 | mol_sum casts data IDs to strings but not mapping IDs | Fixed |
| `PV-BUG-014` | P2/P3 | null mapping targets are aggregated into a null output ID | Fixed |
| `PV-BUG-015` | P2/P3 | duplicated mapping pairs duplicate the input value before aggregation | Fixed |
| `PV-BUG-016` | P2/P3 | entrez_gnodes is unused and species prefixes are always stripped | Changed interface/behavior |
| `PV-BUG-017` | P2/P3 | negative experiment count is silently accepted | Still reproducible |
| `PV-BUG-018` | P2/P3 | decimal strings are parsed as hexadecimal numbers | Changed interface/behavior |
| `PV-BUG-019` | P2/P3 | namespace-qualified KGML child tags are not dispatched | Fixed |
| `PV-BUG-020` | P2/P3 | duplicate KGML entry IDs silently overwrite earlier entries | Still reproducible |
| `PV-BUG-021` | P2/P3 | line graphics coords are ignored and replaced with zero/default geometry | Still reproducible |
| `PV-BUG-022` | P2/P3 | node_info(empty pathway) has no stable columns/schema | Fixed |
| `PV-BUG-023` | P1 | parser locates a namespaced map but searches its glyphs/arcs without namespace | Fixed |
| `PV-BUG-024` | P2/P3 | SBGN namespace is hard-coded to 0.2 and does not accept other valid versions | Fixed |
| `PV-BUG-025` | P2/P3 | nested state-variable glyph is also promoted to a top-level biological node | Fixed |
| `PV-BUG-026` | P2/P3 | standard &lt;clone/&gt; element is not detected; code checks an attribute instead | Fixed |
| `PV-BUG-027` | P2/P3 | Bezier control &lt;point&gt; children inside SBGN &lt;next&gt; are discarded | Still reproducible |
| `PV-BUG-028` | P2/P3 | empty SBGN conversion returns a schema-less DataFrame | Fixed |
| `PV-BUG-029` | P1 | compound y coordinates are flipped while gene y coordinates are effectively not | Fixed |
| `PV-BUG-030` | P1 | compound KGML width is treated as radius instead of diameter | Fixed |
| `PV-BUG-031` | P2/P3 | compound height is ignored and all compounds are forced to width-based circles | Fixed |
| `PV-BUG-032` | P2/P3 | documented/default named highlight colors are parsed as six-digit hex | Fixed |
| `PV-BUG-033` | P2/P3 | three-digit CSS hex colors are not accepted | Fixed |
| `PV-BUG-034` | P1 | bbox_inches='tight' crops/rescales native output instead of preserving KEGG pixels | Still reproducible |
| `PV-BUG-035` | P2/P3 | SVG document title is not XML-escaped | Fixed |
| `PV-BUG-036` | P2/P3 | SVG clip IDs interpolate unescaped node identifiers | Fixed |
| `PV-BUG-037` | P2/P3 | empty SVG fill list renders text but no node shape | Fixed |
| `PV-BUG-038` | P1 | graph/PDF renderer uses only the first experiment color | Still reproducible |
| `PV-BUG-039` | P1 | highlights flip y but native gene painting does not, so borders miss noncentral nodes | Fixed |
| `PV-BUG-040` | P2/P3 | highlight opacity argument is ignored | Fixed |
| `PV-BUG-041` | P2/P3 | change_labels records metadata but does not alter the saved image | Fixed |
| `PV-BUG-042` | P2/P3 | edge highlighting builds positions from genes only | Fixed |
| `PV-BUG-043` | P2/P3 | requested one-pixel line is drawn two pixels thick | Fixed |
| `PV-BUG-044` | P2/P3 | save() does not infer PDF from path and writes PNG bytes to a .pdf name | Fixed |
| `PV-BUG-045` | P1 | duplicated phantom/repeated Catmull-Rom points cause zero denominators and NaNs | Fixed |
| `PV-BUG-046` | P2/P3 | obstacles=None forces every routing mode to a straight two-point line | Fixed |
| `PV-BUG-047` | P2/P3 | obstacles argument is not consulted by routing implementation | Changed interface/behavior |
| `PV-BUG-048` | P2/P3 | orthogonal routing delegates to broken Catmull-Rom implementation | Fixed |
| `PV-BUG-049` | P2/P3 | unknown routing mode silently falls back to straight | Still reproducible |
| `PV-BUG-050` | P2/P3 | smooth_path_svg tension parameter is unused | Fixed |
| `PV-BUG-051` | P2/P3 | nonfinite curve values are serialized directly into SVG | Fixed |
| `PV-BUG-052` | P1 | CLI unconditionally calls gene_data.cast even for compound-only input | Fixed |
| `PV-BUG-053` | P2/P3 | CLI reports pathway row count as 'nodes mapped', including null rows | Fixed |
| `PV-BUG-054` | P2/P3 | upstream feature script fails when run directly because of relative imports | Fixed |
| `PV-BUG-055` | P2/P3 | promised common-name lookup requires exact equality with full KEGG description | Fixed |
| `PV-BUG-056` | P2/P3 | invalid KEGG file types fail with internal KeyError instead of validation error | Still reproducible |
| `PV-BUG-057` | P2/P3 | KEGG downloader trusts any HTTP 200 body without format/content validation | Still reproducible |
| `PV-BUG-058` | P1 | MyGene batch endpoint is /v3/query, not coded /v3/querymany | Fixed |
| `PV-BUG-059` | P2/P3 | nested MyGene fields are stringified as Python dicts instead of extracting IDs | Fixed |
| `PV-BUG-060` | P2/P3 | core forwards KEGG code 'hsa' where MyGene documents common names/taxonomy IDs | Fixed |
| `PV-BUG-061` | P2/P3 | KEGG chemical conversion uses alias 'cpd' where API specifies 'compound' | Still reproducible |
| `PV-BUG-062` | P2/P3 | already-prefixed compound IDs receive a duplicate source prefix | Still reproducible |
| `PV-BUG-063` | P2/P3 | SMP prefix detection accepts malformed arbitrary IDs | Fixed |
| `PV-BUG-064` | P2/P3 | database detection is unexpectedly case-sensitive | Still reproducible |
| `PV-BUG-065` | P1 | SBGN downloaders accept HTTP 200 HTML pages as successful pathway files | Fixed |
| `PV-BUG-066` | P2/P3 | list_reactome_pathways hardcodes Homo sapiens in URL | Fixed |
| `PV-BUG-067` | P2/P3 | SVG output unnecessarily requires/downloads a KEGG PNG when kegg_native=True | Changed interface/behavior |
| `PV-BUG-068` | P2/P3 | KGML shape='circle' is sent to SVG but only shape='ellipse' renders an ellipse | Fixed |
| `PV-BUG-069` | P2/P3 | all-transparent SVG nodes are forcibly recolored gray | Still reproducible |
| `PV-BUG-070` | P2/P3 | compound-only native color-key layout leaves a blank visible ticked subplot | Fixed |
| `PV-BUG-071` | P2/P3 | graph color key always uses gene limits/colors, even for compound-only plots | Fixed |
| `PV-BUG-072` | P2/P3 | highlight drawing cannot assign RGB tuples into RGBA arrays | Fixed |
| `PV-BUG-073` | P2/P3 | dynamic label-change metadata is lost when another layer is chained | Fixed |
| `PV-BUG-074` | P1 | Reactome SBGN file exporter route is coded as /exporter/sbgn/{id}.sbgn instead of /exporter/event/{id}.sbgn | Still reproducible |
| `PV-BUG-075` | P1 | _add_symbol_labels joins a SYMBOL column but never replaces the rendered label | Still reproducible |
| `PV-BUG-076` | P2/P3 | invalid node_sum ValueError is swallowed by node_map and core still returns output | Fixed |
| `PV-BUG-077` | P2/P3 | --simulate branch silently ignores a supplied --cpd-data file | Changed interface/behavior |
| `PV-BUG-078` | P2/P3 | MyGene returnall dictionary response is iterated as if it were a list of hits | Fixed |
| `PV-BUG-079` | P2/P3 | wordwrap width=0 with break_word=True makes no progress and loops forever | Fixed |
| `PV-FEATURE-001` | P2/P3 | discrete is accepted by public APIs but ignored by node_color | Fixed |
| `PV-FEATURE-002` | P2/P3 | SBGNGlyph exposes unit_of_information but parser never populates it | Fixed |
| `PV-FEATURE-003` | P1 | main SVG renderer receives no relation data and emits no pathway edges | Fixed |
| `PV-FEATURE-004` | P1 | graph renderer builds nodes only; KGML relations are not passed into it | Fixed |
| `PV-FEATURE-005` | P2/P3 | PANTHER downloader is an explicit unimplemented stub | Fixed |
| `PV-FEATURE-006` | P2/P3 | SMPDB downloader is an explicit unimplemented stub | Fixed |
| `PV-FEATURE-007` | P1 | non-KEGG database detection/download/parsing is not wired through pathview() | Changed interface/behavior |
