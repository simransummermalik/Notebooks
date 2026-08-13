# Pathview Plus v3 change audit

**Audit date:** August 11, 2026  
**Previous audited commit:** `07aee813375347bcc933ad21b4aed561dd7cd3bf`  
**Current commit checked:** `d4d45decec56e1ebec15cf04ae62ff944851780e`  
**Current package version:** `3.1.0`

## Bottom line

I compared every one of the 86 findings in the August 10 audit with the current v3.1.0 source, current upstream tests, and adapted v3 rechecks.

| Status | Count | Meaning |
|---|---:|---|
| Fixed | 60 | The old failure condition is gone in a current test, adapted recheck, or direct source check. |
| Still reproducible | 19 | I could still demonstrate the old failure condition in v3.1.0. |
| Changed | 7 | The interface or documented behavior was replaced, so the old test is no longer like-for-like. |
| Not retested | 0 | Every old finding received one of the three determinate classifications above. |

This is a major improvement over the version audited on August 10. The rewrite fixes the most fundamental problems: offline species lookup, namespaced SBGN parsing, real graph edges, usable `PathwayResult` highlighting, compound-only CLI use, stable parser schemas, correct compound coordinates and radius, and the Catmull-Rom NaN failure.

I would not call all of the old findings closed yet. Five of the remaining reproducible findings were P1 findings in the original audit: `PV-BUG-006`, `PV-BUG-034`, `PV-BUG-038`, `PV-BUG-074`, and `PV-BUG-075`.

## What I ran

I first verified the two exact Git commits, then read `CHANGELOG.md`, `PARITY.md`, the v3 source, all current upstream tests, and the previous `BUGS.json`.

The current upstream suite collected 327 tests:

| Result | Count |
|---|---:|
| Passed | 320 |
| Failed | 1 |
| Skipped | 6 |

**Final environment-normalized rerun:** after this restricted-workspace
preflight, I reran the complete unchanged suite with access to the normal user
cache. That authoritative run finished with **321 passed, 6 skipped, and 0
failed**. Its JUnit file is `results/pathview-plus-v3-upstream-junit.xml`. The
320/1/6 table below describes the preserved sandbox preflight, not a final code
failure.

The one failure was `TestCliRobustness::test_piping_output_does_not_traceback`. It was caused by the restricted workspace, not by the pipe behavior under test. That test creates a subprocess environment containing only `PATH` and `PYTHONPATH`; the child process therefore tried to create `/Users/summermalik/.cache/pathview-plus`, which this workspace blocks. The same pipe command completed normally when I supplied `XDG_CACHE_HOME=/tmp/pathview-v3-cache`:

```text
pathview-plus 3.1.0
organisms bundled : 10,718
```

The six skips were one optional-dependency branch because SciPy is installed, three live SBGN collection downloads that require `PATHVIEW_TEST_NETWORK=1`, and two RData tests whose source fixture was absent.

The current JUnit result is in `results/v3-audit/upstream-tests.xml`.

## Important findings that remain

### Remaining P1 findings

| ID | What I observed in v3.1.0 |
|---|---|
| `PV-BUG-006` | `map_null=False` is not passed into `node_map()`. With one matched gene, `plot_data_gene` still contained 27 pathway rows, while only one row carried a value. |
| `PV-BUG-034` | A 120 x 100 native background became a 792 x 664 saved PNG even with the title, key, and signature disabled at 100 dpi. Native output is still composed through a Matplotlib figure and saved with `bbox_inches="tight"` (`lib/rendering.py:240-269`). |
| `PV-BUG-038` | Graph rendering still selects `cols[0]` for every node (`lib/graph_rendering.py:157-162`). A two-condition node therefore becomes one flat graph-node color instead of preserving both states. |
| `PV-BUG-074` | `REACTOME_SBGN` is still `https://reactome.org/ContentService/exporter/sbgn` and the downloader constructs `.../sbgn/{id}.sbgn` (`lib/constants.py:17`, `lib/databases.py:130`). This is the same route identified in the old finding. |
| `PV-BUG-075` | `_symbol_labels()` only attempts conversion when the existing label is blank (`lib/pathview.py:470-478`). A node whose label is the Entrez text `7157` produced an empty label map instead of `TP53`. |

### Remaining P2/P3 findings

| ID | Adapted v3 result |
|---|---|
| `PV-BUG-003` | The Python API still has no closed validation for `output_format`. It accepted `jpg` and uppercase `PNG`, while empty input failed later as `FileNotFoundError` and `banana` failed later inside Matplotlib. The CLI does validate its choices. |
| `PV-BUG-007` | `min_nnodes` is checked against positioned layout nodes before data mapping (`lib/pathview.py:266-275`). A completely unmatched ID still returned a truthy result with 64 layout nodes. |
| `PV-BUG-010` | `pathview("mmu00020", species="hsa")` still formed `hsammu00020` (`lib/pathview.py:204-207`) instead of rejecting the conflict. |
| `PV-BUG-017` | `sim_mol_data(..., n_exp=-1)` still silently creates `exp1` because the loop uses `max(1, int(n_exp))` (`lib/mol_data.py:328-330`). |
| `PV-BUG-020` | Duplicate KGML entry IDs still overwrite earlier entries in the node dictionary (`lib/kgml_parser.py:290-296`). |
| `PV-BUG-021` | KGML line `coords` are still ignored. The adapted line example returned `x=None`, `y=None`, `width=46`, and `height=17` (`lib/kgml_parser.py:179-189`). |
| `PV-BUG-027` | SBGN `<point>` control children inside `<next>` are still omitted. `_parse_spline()` reads only the `<next>` element's own `x` and `y` (`lib/sbgn_parser.py:315-326`). |
| `PV-BUG-049` | An unknown spline mode such as `banana` still falls through to the curved route and returns a `(30, 2)` curve (`lib/splines.py:179-204`). |
| `PV-BUG-056` | `download_kegg(..., file_type=["banana"])` still raises the internal `KeyError('banana')` at the target lookup (`lib/databases.py:75-76`). |
| `PV-BUG-057` | XML responses now receive a content check, but PNG responses do not. A mocked HTTP 200 HTML body was written to `hsa00020.png` and reported as `succeed` (`lib/databases.py:81-96`). |
| `PV-BUG-061` | The compound conversion URL still uses `/conv/cpd/` rather than the database name from the old finding (`lib/id_mapping.py:370-377`). |
| `PV-BUG-062` | Already-prefixed compound input is still prefixed a second time. `pubchem:123` produced `/conv/cpd/pubchem:pubchem:123`. |
| `PV-BUG-064` | Database detection is still case-sensitive. Uppercase Reactome and PANTHER IDs resolved, while lowercase forms returned `None` (`lib/databases.py:341-358`). |
| `PV-BUG-069` | SVG rendering still replaces a transparent fill with the theme's unmapped color (`lib/svg_rendering.py:87-91`). |

## Findings whose interface changed

I did not label these fixed or still broken because v3 replaced the relevant contract.

| ID | What changed |
|---|---|
| `PV-BUG-005` | The old parallel molecule-type color dictionaries were replaced by separate `ColorScale` objects and `gene_color` / `cpd_color` settings. Partial `ColorScale` dictionaries now merge with defaults, but the old `low={"gene": ...}` call is no longer the same API. |
| `PV-BUG-016` | The old `entrez_gnodes` switch was removed. KEGG identifiers are now normalized during parsing and the node mapper uses the parsed `kegg_names` list. |
| `PV-BUG-018` | String value columns are no longer parsed as hexadecimal numbers. `node_color()` now maps numeric columns only, so a numeric-looking string column is excluded instead of being treated like a numeric column. |
| `PV-BUG-047` | Obstacle behavior now has a separate documented `routing_mode="avoid"`; ordinary `curved` routing is not documented to inspect obstacles (`lib/splines.py:167-198`). |
| `PV-BUG-067` | Output choice is now explicit through `render_mode`. `render_mode="svg"` needs only KGML, while `auto` and `native` may request the PNG (`lib/pathview.py:233-238`). |
| `PV-BUG-077` | The old CLI `--simulate` branch was removed. Simulation remains available through the Python data-generation functions rather than as that CLI branch. |
| `PV-FEATURE-007` | Non-KEGG work is now handled by a separate `sbgnview()` / `sbgnview_batch()` orchestrator instead of dispatching Reactome and other IDs through `pathview()`. |

## Fixed finding index

The following 60 old findings are fixed under the definition used in this audit:

```text
PV-BUG-001  PV-BUG-002  PV-BUG-004  PV-BUG-008  PV-BUG-009
PV-BUG-011  PV-BUG-012  PV-BUG-013  PV-BUG-014  PV-BUG-015
PV-BUG-019  PV-BUG-022  PV-BUG-023  PV-BUG-024  PV-BUG-025
PV-BUG-026  PV-BUG-028  PV-BUG-029  PV-BUG-030  PV-BUG-031
PV-BUG-032  PV-BUG-033  PV-BUG-035  PV-BUG-036  PV-BUG-037
PV-BUG-039  PV-BUG-040  PV-BUG-041  PV-BUG-042  PV-BUG-043
PV-BUG-044  PV-BUG-045  PV-BUG-046  PV-BUG-048  PV-BUG-050
PV-BUG-051  PV-BUG-052  PV-BUG-053  PV-BUG-054  PV-BUG-055
PV-BUG-058  PV-BUG-059  PV-BUG-060  PV-BUG-063  PV-BUG-065
PV-BUG-066  PV-BUG-068  PV-BUG-070  PV-BUG-071  PV-BUG-072
PV-BUG-073  PV-BUG-076  PV-BUG-078  PV-BUG-079
PV-FEATURE-001  PV-FEATURE-002  PV-FEATURE-003
PV-FEATURE-004  PV-FEATURE-005  PV-FEATURE-006
```

Some especially important verified fixes are:

- Offline species resolution now uses the bundled organism table, and common names resolve correctly.
- `pathview()` now returns a composable `PathwayResult` with a correctly located raster frame.
- `kegg_names` survives parsing and mapping, so highlighting can resolve biological IDs.
- `max_abs` and seeded `random` aggregation work; mapping IDs are normalized; null targets and duplicate pairs are removed.
- Namespaced KGML and SBGN parse correctly. State variables and units of information remain auxiliary metadata, clone markers work, and empty parser outputs have stable schemas.
- Compound y coordinates and radii are corrected, named and short colors parse, SVG titles are escaped, empty SVG fills produce a visible node, and SVG/graph renderers receive real edge tables.
- Highlight opacity, visible label changes, compound edge highlighting, PDF save inference, RGBA handling, and chained label metadata now work.
- Compound-only CLI runs work, the upstream feature script runs directly, species common names resolve, MyGene uses `querymany`, nested results are unpacked, and KEGG species codes are translated to taxonomy IDs.
- PANTHER and SMPDB are no longer silent stubs. They use the indexed SBGN collection, and the current capability tests confirm that all declared downloaders are real callables.

## Important test interpretation

I also attempted the August 10 test modules against v3.1.0. Those files are useful historical evidence, but they cannot be treated as a drop-in v3 regression suite. The rewrite removed or renamed private helpers such as `_hex_to_rgb255`, changed `PathwayResult` construction to carry a `RasterFrame`, removed `pathview.kegg_api`, and replaced the old CLI layout. As a result, many old tests fail during import, fixture setup, or monkeypatching before reaching the behavior they were meant to check.

I saved those compatibility attempts as JUnit files in `results/v3-audit/`. I classified an old finding only after checking its current equivalent, not merely from whether the version-specific old xfail happened to pass or fail.

## Suggested order for the next pass

1. Fix the five remaining P1 findings: `006`, `034`, `038`, `074`, and `075`.
2. Add direct v3 regression tests for all 19 reproducible findings so they cannot be hidden by the rewritten API.
3. Validate `output_format`, download `file_type`, species/pathway-prefix combinations, negative simulation counts, and spline routing modes at the public boundary.
4. Validate downloaded PNG bytes before writing them, normalize compound prefixes before building KEGG URLs, and make database detection case-insensitive.
5. Decide and document whether transparent SVG nodes should truly be transparent or intentionally use the theme's unmapped color.

## Machine-readable result

The complete status mapping, counts, exact commits, adapted evidence, and artifact list are in:

`results/v3-audit/old-findings-status.json`
