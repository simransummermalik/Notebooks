# Sixty August 10 failure conditions not reproduced in Pathview Plus 3.1.0

These 60 IDs were classified Fixed in the v3.1.0 recheck. Fixed is narrow here: the exact old failure condition was absent at commit `d4d45de`, based on a current test, an adapted check, or source inspection. It is not a claim that the entire surrounding feature is defect-free. Fourteen of these were original P1 findings and 46 were P2/P3.

Examples include offline cached species resolution (`PV-BUG-004`), a composable result with identifiers and aligned highlights (`PV-BUG-008`, `PV-BUG-009`, `PV-BUG-039`), namespace-aware SBGN parsing (`PV-BUG-023`), corrected compound geometry (`PV-BUG-029` through `PV-BUG-031`), edges in SVG and graph outputs (`PV-FEATURE-003`, `PV-FEATURE-004`), and compound-only CLI input (`PV-BUG-052`).

| ID | August 10 priority | Failure condition that was absent in v3.1.0 |
|---|---|---|
| `PV-BUG-001` | P2/P3 | setup.py/distribution is 2.0.2 but pathview.__version__ is 2.0.0 |
| `PV-BUG-002` | P2/P3 | --no-kegg-native with output_format='png' silently writes graph PDF |
| `PV-BUG-004` | P1 | cached files cannot bypass live species lookup |
| `PV-BUG-008` | P1 | core returns dict while documented highlighting requires PathwayResult |
| `PV-BUG-009` | P1 | mapped node table drops the exploded kegg_names identifier |
| `PV-BUG-011` | P2/P3 | empty KGML produces a schema-less frame and core crashes before graceful skip |
| `PV-BUG-012` | P1 | group aggregation UDF receives scalar elements under current Polars |
| `PV-BUG-013` | P2/P3 | mol_sum casts data IDs to strings but not mapping IDs |
| `PV-BUG-014` | P2/P3 | null mapping targets are aggregated into a null output ID |
| `PV-BUG-015` | P2/P3 | duplicated mapping pairs duplicate the input value before aggregation |
| `PV-BUG-019` | P2/P3 | namespace-qualified KGML child tags are not dispatched |
| `PV-BUG-022` | P2/P3 | node_info(empty pathway) has no stable columns/schema |
| `PV-BUG-023` | P1 | parser locates a namespaced map but searches its glyphs/arcs without namespace |
| `PV-BUG-024` | P2/P3 | SBGN namespace is hard-coded to 0.2 and does not accept other valid versions |
| `PV-BUG-025` | P2/P3 | nested state-variable glyph is also promoted to a top-level biological node |
| `PV-BUG-026` | P2/P3 | standard &lt;clone/&gt; element is not detected; code checks an attribute instead |
| `PV-BUG-028` | P2/P3 | empty SBGN conversion returns a schema-less DataFrame |
| `PV-BUG-029` | P1 | compound y coordinates are flipped while gene y coordinates are effectively not |
| `PV-BUG-030` | P1 | compound KGML width is treated as radius instead of diameter |
| `PV-BUG-031` | P2/P3 | compound height is ignored and all compounds are forced to width-based circles |
| `PV-BUG-032` | P2/P3 | documented/default named highlight colors are parsed as six-digit hex |
| `PV-BUG-033` | P2/P3 | three-digit CSS hex colors are not accepted |
| `PV-BUG-035` | P2/P3 | SVG document title is not XML-escaped |
| `PV-BUG-036` | P2/P3 | SVG clip IDs interpolate unescaped node identifiers |
| `PV-BUG-037` | P2/P3 | empty SVG fill list renders text but no node shape |
| `PV-BUG-039` | P1 | highlights flip y but native gene painting does not, so borders miss noncentral nodes |
| `PV-BUG-040` | P2/P3 | highlight opacity argument is ignored |
| `PV-BUG-041` | P2/P3 | change_labels records metadata but does not alter the saved image |
| `PV-BUG-042` | P2/P3 | edge highlighting builds positions from genes only |
| `PV-BUG-043` | P2/P3 | requested one-pixel line is drawn two pixels thick |
| `PV-BUG-044` | P2/P3 | save() does not infer PDF from path and writes PNG bytes to a .pdf name |
| `PV-BUG-045` | P1 | duplicated phantom/repeated Catmull-Rom points cause zero denominators and NaNs |
| `PV-BUG-046` | P2/P3 | obstacles=None forces every routing mode to a straight two-point line |
| `PV-BUG-048` | P2/P3 | orthogonal routing delegates to broken Catmull-Rom implementation |
| `PV-BUG-050` | P2/P3 | smooth_path_svg tension parameter is unused |
| `PV-BUG-051` | P2/P3 | nonfinite curve values are serialized directly into SVG |
| `PV-BUG-052` | P1 | CLI unconditionally calls gene_data.cast even for compound-only input |
| `PV-BUG-053` | P2/P3 | CLI reports pathway row count as 'nodes mapped', including null rows |
| `PV-BUG-054` | P2/P3 | upstream feature script fails when run directly because of relative imports |
| `PV-BUG-055` | P2/P3 | promised common-name lookup requires exact equality with full KEGG description |
| `PV-BUG-058` | P1 | MyGene batch endpoint is /v3/query, not coded /v3/querymany |
| `PV-BUG-059` | P2/P3 | nested MyGene fields are stringified as Python dicts instead of extracting IDs |
| `PV-BUG-060` | P2/P3 | core forwards KEGG code 'hsa' where MyGene documents common names/taxonomy IDs |
| `PV-BUG-063` | P2/P3 | SMP prefix detection accepts malformed arbitrary IDs |
| `PV-BUG-065` | P1 | SBGN downloaders accept HTTP 200 HTML pages as successful pathway files |
| `PV-BUG-066` | P2/P3 | list_reactome_pathways hardcodes Homo sapiens in URL |
| `PV-BUG-068` | P2/P3 | KGML shape='circle' is sent to SVG but only shape='ellipse' renders an ellipse |
| `PV-BUG-070` | P2/P3 | compound-only native color-key layout leaves a blank visible ticked subplot |
| `PV-BUG-071` | P2/P3 | graph color key always uses gene limits/colors, even for compound-only plots |
| `PV-BUG-072` | P2/P3 | highlight drawing cannot assign RGB tuples into RGBA arrays |
| `PV-BUG-073` | P2/P3 | dynamic label-change metadata is lost when another layer is chained |
| `PV-BUG-076` | P2/P3 | invalid node_sum ValueError is swallowed by node_map and core still returns output |
| `PV-BUG-078` | P2/P3 | MyGene returnall dictionary response is iterated as if it were a list of hits |
| `PV-BUG-079` | P2/P3 | wordwrap width=0 with break_word=True makes no progress and loops forever |
| `PV-FEATURE-001` | P2/P3 | discrete is accepted by public APIs but ignored by node_color |
| `PV-FEATURE-002` | P2/P3 | SBGNGlyph exposes unit_of_information but parser never populates it |
| `PV-FEATURE-003` | P1 | main SVG renderer receives no relation data and emits no pathway edges |
| `PV-FEATURE-004` | P1 | graph renderer builds nodes only; KGML relations are not passed into it |
| `PV-FEATURE-005` | P2/P3 | PANTHER downloader is an explicit unimplemented stub |
| `PV-FEATURE-006` | P2/P3 | SMPDB downloader is an explicit unimplemented stub |
