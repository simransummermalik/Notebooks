# Pathview Plus technical findings

**Snapshot:** commit `07aee813375347bcc933ad21b4aed561dd7cd3bf`  
**Environment:** Python 3.14.3, Pathview Plus distribution 2.0.2, runtime
`__version__` 2.0.0, Polars 1.43.2  
**What I used:** I read the source, ran 239 repeatable offline test cases, used
a saved official KEGG `hsa04110` pathway and controlled HTTP responses, and
wrote down the live website checks separately.

## How I classified the results

I call a finding confirmed when I can see the issue in the current source code
and reproduce it locally. I list something as a feature gap when the code says
it is reserved or not implemented, or when advertised parts exist but are not
connected. I recorded provider availability separately so an outside service
cannot make the offline test suite pass or fail.

## P1 findings

### Core result and data contract

1. **PV-BUG-004 — cache is not offline-capable.** I confirmed that species
   resolution happens before the filename cache check. This means valid cached
   XML/PNG files still cannot run when the organism-list service is unavailable.
   Source:
   [`pathview.py:127-157`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/pathview.py#L127-L157).

2. **PV-BUG-006 — `map_null=False` does not filter null joined rows.** I found
   that this setting only changes the result when a whole molecular table is
   `None`. If a table is present, unmatched pathway nodes remain after the left
   join. Source:
   [`pathview.py:264-302`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/pathview.py#L264-L302),
   [`node_mapping.py:93-99`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/node_mapping.py#L93-L99).

3. **PV-BUG-008/PV-BUG-009 — core/highlighting interface mismatch.** The core
   returns a `dict`, but the highlighting layers require a `PathwayResult`. The
   mapped join also removes `kegg_names`, even though highlighting and symbol
   conversion both need that column. Source:
   [`pathview.py:232`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/pathview.py#L232),
   [`node_mapping.py:93-99`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/node_mapping.py#L93-L99),
   [`highlighting.py:47-81`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/highlighting.py#L47-L81).

4. **PV-BUG-075 — symbols are not used as rendered labels.** I tested this
   with a controlled successful mapping. `_add_symbol_labels()` joins a
   `SYMBOL` column, but it never assigns that value to `label`. Source:
   [`pathview.py:305-315`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/pathview.py#L305-L315).

5. **PV-BUG-012 — two advertised aggregation modes raise.** Under Polars
   1.43.2, the `max_abs` and `random` group UDFs call `.to_numpy()` on scalar
   elements. Both modes raise instead of returning an aggregation. Source:
   [`mol_data.py:25-44`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/mol_data.py#L25-L44).

### Rendering correctness

6. **PV-BUG-029/PV-BUG-030 — compound center and size are wrong.** I found
   three connected geometry problems: compound `y` is flipped relative to
   genes, `width` is treated as the radius, and `height` is ignored. Source:
   [`rendering.py:119-146`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/rendering.py#L119-L146).

7. **PV-BUG-034 — native canvas dimensions change.** The frozen KEGG image is
   1039 × 801, but the rendered image becomes 835 × 646. This happens because
   the image is put inside a Matplotlib figure and saved with
   `bbox_inches="tight"`. Source:
   [`rendering.py:195-225`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/rendering.py#L195-L225).

8. **PV-FEATURE-003/PV-FEATURE-004 — vector renderers omit relations.** I
   checked both vector paths. The core does not pass parsed relations to either
   renderer. The graph renderer calls `add_node` but never `add_edge`, and the
   SVG renderer never calls its own `render_edge_svg()` helper. Frozen
   `hsa04110` parsed 79 relations; both outputs contained zero pathway edges.
   Source:
   [`rendering.py:280-315`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/rendering.py#L280-L315),
   [`svg_rendering.py:195-291`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/svg_rendering.py#L195-L291).

9. **PV-BUG-038 — PDF uses only state one.** The renderer selects the first
   `*_col` column and does not use any later experiment columns. Source:
   [`rendering.py:270-278`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/rendering.py#L270-L278).

10. **PV-BUG-039 — highlights miss noncentral native nodes.** Highlighting
    flips the KGML `y` coordinate, while native gene painting effectively uses
    the coordinate without that flip. The mismatch moves highlights away from
    noncentral nodes. Source:
    [`highlighting.py:302-348`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/highlighting.py#L302-L348).

### SBGN and provider integrations

11. **PV-BUG-023 — standard namespaced SBGN parses empty.** The parser first
    finds a namespace-qualified map, but then searches for glyph and arc tags
    without the namespace. Source:
    [`sbgn_parser.py:196-258`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/sbgn_parser.py#L196-L258).

12. **PV-FEATURE-007 — the non-KEGG parts are not connected to the main
    function.** I traced the full `pathview()` flow. It always resolves KEGG,
    downloads KEGG, and parses KGML. It never sends a pathway through
    `detect_database()`, the SBGN downloaders, or `parse_sbgn()`. Source:
    [`pathview.py:127-205`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/pathview.py#L127-L205).

13. **PV-BUG-058 — MyGene batch URL is wrong.** The code posts to
    `/v3/querymany`, while the official API documents `POST /v3/query`. Source:
    [`id_mapping.py:32-58`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/id_mapping.py#L32-L58),
    [official MyGene batch documentation](https://docs.mygene.info/en/v3/doc/query_service.html#batch-queries-via-post).

14. **PV-BUG-074 — Reactome SBGN route is wrong.** The code builds
    `/exporter/sbgn/{id}.sbgn`, but the file exporter uses
    `/exporter/event/{id}.sbgn`. Source:
    [`databases.py:29-75`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/databases.py#L29-L75),
    [official Reactome controller](https://github.com/reactome/content-service/blob/8d5b39fd903303163441ebf2ee3998a7c794bebe/src/main/java/org/reactome/server/service/controller/exporter/SbxxExporterController.java#L54-L61).

15. **PV-BUG-065 — HTTP success is accepted without pathway validation.** I
    found that Reactome and MetaCyc can save an HTML response as `.sbgn`. KEGG
    also trusts the returned PNG/XML body without checking that it is the
    expected pathway content. Source:
    [`databases.py:69-125`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/databases.py#L69-L125),
    [`kegg_api.py:124-142`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/kegg_api.py#L124-L142).

### CLI and curves

16. **PV-BUG-052 — compound-only CLI crashes.** The CLI always dereferences
    `gene_data` before it calls the core, even when the user supplied only
    compound data. Source:
    [`pathview-cli.py:209-216`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/bin/pathview-cli.py#L209-L216).

17. **PV-BUG-045 — documented Catmull-Rom output contains NaNs.** Repeated
    phantom endpoints create zero denominators, and orthogonal routing uses the
    same failing calculation. Source:
    [`splines.py:138-169`](https://github.com/raw-lab/pathview-plus/blob/07aee813375347bcc933ad21b4aed561dd7cd3bf/lib/splines.py#L138-L169).

## Additional confirmed groups

I kept the shorter P1 explanations above, but the complete finding-by-finding
results are in [`ALL-FINDINGS.md`](ALL-FINDINGS.md) and
[`BUGS.json`](BUGS.json). They include:

- configuration validation and output dispatch (`PV-BUG-001`–`011`);
- molecule joins, duplicates, prefixes, null targets, simulation, and colors
  (`PV-BUG-012`–`018`, `PV-FEATURE-001`);
- KGML/SBGN schema and metadata edge cases (`PV-BUG-019`–`028`,
  `PV-FEATURE-002`);
- PNG/SVG/PDF shape, XML, transparency, legend, and state behavior
  (`PV-BUG-029`–`038`, `067`–`071`, `PV-FEATURE-003`–`004`);
- highlighting and save behavior (`PV-BUG-039`–`044`, `072`–`073`);
- splines/routing (`PV-BUG-045`–`051`);
- CLI and bundled test runner (`PV-BUG-052`–`054`, `077`);
- provider URLs, species, body validation, and response shapes
  (`PV-BUG-055`–`066`, `074`, `078`);
- argument nontermination guard (`PV-BUG-079`);
- intentionally unimplemented PANTHER/SMPDB downloads
  (`PV-FEATURE-005`–`006`).

## What I would work on next

This is the order I would try because some of the later fixes depend on the
earlier ones:

1. Preserve exact native dimensions and use the same coordinates for genes,
   compounds, and highlights. I would check this by making sure the input and
   output dimensions match and the exact center and ellipse bounds pass for
   noncentral nodes.
2. Repair the core result contract and mapping identifiers. I would check this
   by running the documented `pathview(...) + highlight_nodes(...)` example
   exactly as written.
3. Pass relations into SVG/PDF and preserve all states. I would compare the
   renderer edge count with the parsed relation count for the controlled
   subset, then make sure state two visibly changes the output.
4. Make SBGN namespace-aware and extract biological identifiers. I would use
   frozen official Reactome and SMPDB examples and check that they parse nonzero
   nodes/arcs and map controlled UniProt/ChEBI data.
5. Update provider routes and species handling, then validate MIME types and
   body roots. A mocked HTML 200 response should be rejected, while the optional
   official website checks should pass.
6. Repair the aggregation and curve math. I would check that every advertised
   method is finite, repeatable when seeded, and rejects invalid values clearly.
7. Correct the CLI behavior and the upstream feature suite. I would test
   gene-only, compound-only, combined, simulated, cached/offline, and invalid
   commands with exact exit-code and output checks.

## Reproduction

I used the same local command below to rerun the complete check set:

```bash
cd "pathveiw bug checks"
../pygage-pathview-validation/.venv/bin/python scripts/run_deep_checks.py
```

The run succeeds only when there are no unexpected failures. Confirmed findings
stay visible as strict `xfail` results. If a finding is fixed without updating
the check, it changes to an unexpected XPASS so the result cannot disappear
silently.
