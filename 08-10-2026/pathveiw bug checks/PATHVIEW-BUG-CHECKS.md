# Pathview Plus bug-check summary

**Date checked:** August 10, 2026  
**Repository:** [`raw-lab/pathview-plus`](https://github.com/raw-lab/pathview-plus)  
**Commit tested:** `07aee813375347bcc933ad21b4aed561dd7cd3bf`

## Bottom line

I found that the basic **KEGG gene-data → native PNG** workflow works when I
use controlled cached files. The tests passed for one-condition nodes, the
requested two-condition left/right split, and three-condition ordered slices.

The full package should still be called **beta** for now. I found reproducible,
high-priority issues in compound overlays, SVG/PDF pathway structure,
SBGN/Reactome, ID conversion, and the highlighting workflow shown in the
documentation. I would not describe those parts as fully validated until the
P1 findings are fixed.

I wrote these results down so I can rerun the same examples while checking the
package and explaining the results in the paper.

## Exact result

| Result | Count |
|---|---:|
| Total test cases | 239 |
| Passed | 143 |
| Known-bug reproductions | 89 test cases |
| Feature-gap reproductions | 7 test cases |
| Unique reproducible code findings | 79 |
| Unique feature gaps | 7 |
| New or unexplained failures in the test run | **0** |

Most of the 79 findings are smaller P2/P3 checks involving malformed files,
rare identifiers, unusual color inputs, and API boundaries. I put the smaller
P1 group first because those findings affect the main workflows more directly.

## What worked

- All 53 declared public exports imported.
- All package modules compiled.
- Cached KEGG `hsa04110` parsed: 115 nodes and 79 relations.
- Native PNG rendered with one, two, and three gene conditions.
- Two conditions appeared in the expected order: the first condition on the
  left and the second condition on the right.
- Ordinary numeric color mapping, clipping, missing values, asymmetric limits,
  and transformations worked.
- `sum`, `mean`, `median`, and `max` aggregation worked.
- Ordinary unnamespaced KGML and controlled unnamespaced SBGN parsed.
- Ordinary SVG was valid XML and escaped label text.
- Explicit graph PDF produced a valid PDF file.
- Explicit six-digit-hex highlighting worked on a manually constructed
  `PathwayResult`.
- Cubic and quadratic Bezier helpers produced finite curves and correct
  endpoints.
- CLI help, argument choices, and combined gene/compound table loading worked.
- Repeating the same native render made the same image each time.

## Things I would check first

### 1. Compound overlays can be biologically misleading

Genes and compounds do not use the same vertical coordinate rule. On the same
100-pixel image, a gene at `y=20` is painted near row 20, but a compound at
`y=20` is painted near row 80. The compound `width` is also treated as a radius
instead of the full diameter, and its `height` is ignored. This can put a
compound in the wrong place and make it the wrong size.

**Recommendation:** correct and pixel-test the compound center, width, height,
and multi-state split before validating compound or multi-omics output.

### 2. Native output changes the KEGG canvas size

The official frozen `hsa04110` background is **1039 × 801**, but each Python
output was **835 × 646**, even when I disabled the signature and color key.
The Matplotlib tight bounding box rescales or crops the painted image. Because
of that change, the original KGML coordinates also do not line up with
post-render highlighting.

**Recommendation:** save the painted pixel array directly when no extra margin
is requested, or guarantee an exact coordinate transform in the returned
result.

### 3. SVG and PDF omit the pathway connections

The frozen pathway has 79 parsed relations. The generated SVG and PDF graph
receive only node data, so neither one contains the KGML relation edges. The
PDF also uses only the first condition's color.

**Recommendation:** pass parsed relations/reactions into both renderers, test
edge counts, and define a real multi-state PDF node design.

### 4. Reactome/SBGN is not an end-to-end workflow yet

The main `pathview()` function only handles KEGG. If it receives a
Reactome ID, it turns that ID into an invalid KEGG-style ID. The Reactome SBGN
route is outdated, and standard namespaced SBGN files parse as zero
glyphs/arcs. The program also needs to extract biological IDs before it can map
user data to SBGN nodes.

**Recommendation:** build a separate flow for each database:

`detect database → download/validate file → namespace-aware parser → biological ID mapping → renderer`

### 5. The documented highlighting composition is disconnected

The main `pathview()` function returns a plain dictionary, but
`highlight_nodes()` and the other highlighting layers require a
`PathwayResult`. Normal mapped gene tables also lose the `kegg_names` column
that those layers need. After that, named default colors such as `red` fail in
the low-level color parser, and highlights away from the center use the wrong
vertical coordinate.

**Recommendation:** make the core return one complete `PathwayResult` that
contains the raw image, output path, stable node IDs, and coordinate metadata.
Then test the README example exactly as it is written.

### 6. Several advertised options currently fail or silently do something else

- `max_abs` and `random` aggregation raise with current supported Polars.
- An invalid `node_sum` is swallowed and can still produce a successful-looking
  output without the intended gene layer.
- Compound-only CLI input crashes before reaching the core.
- Default Catmull-Rom and orthogonal routes contain non-finite values.
- Unknown Python `output_format` values silently produce PDF.

### 7. External ID routes need updates

- MyGene batch queries use `/v3/querymany`; the official batch endpoint is
  `/v3/query`.
- KEGG species codes such as `hsa` must be translated to a MyGene-supported
  common name or taxonomy ID.
- Reactome's SBGN file route should use `/exporter/event/{id}.sbgn`.
- Successful HTTP bodies need MIME/signature/XML validation so an HTML error or
  login page is not saved as a pathway.

## How I would describe the current version

If someone asks which parts are working right now, I would describe it this
way:

> Pathview Plus beta currently supports controlled KEGG gene-data overlays on
> native pathway PNGs, including multiple conditions. SVG, graph/PDF,
> compound/multi-omics, highlighting, SBGN, and additional database integrations
> are under active validation.

This description stays close to what I was able to reproduce in the tests and
does not include the parts that still need more work.

## Where every detail is stored

- [`pathview_deep_bug_checks.executed.ipynb`](pathview_deep_bug_checks.executed.ipynb)
  — visual walkthrough with saved cell output.
- [`TECHNICAL-FINDINGS.md`](TECHNICAL-FINDINGS.md) — source locations and more
  detail for someone working on the code.
- [`ALL-FINDINGS.md`](ALL-FINDINGS.md) — every reproduced ID in one Markdown
  appendix.
- [`BUGS.json`](BUGS.json) — every finding and exact reproducing test.
- [`FEATURE-TEST-MATRIX.csv`](FEATURE-TEST-MATRIX.csv) — coverage by behavior.
- [`results/audit-results.csv`](results/audit-results.csv) — all 239 outcomes.
- [`results/pytest-output.txt`](results/pytest-output.txt) — raw test log.
- [`results/evidence/`](results/evidence/) — frozen files, images, SVG, PDF, and
  numerical evidence.
- [`EXTERNAL-SERVICE-OBSERVATIONS.md`](EXTERNAL-SERVICE-OBSERVATIONS.md) — live
  provider observations kept separate from offline code findings.
