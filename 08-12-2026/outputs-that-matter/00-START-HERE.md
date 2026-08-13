# Selected handoff files

This folder is the quick handoff for the August 12 Pathview Plus comparison. The full source evidence remains in the dated August 10 and August 11 folders; these files are labeled copies and new comparison outputs.

## Recommended order

1. Read [`../COMPARISON-SUMMARY.md`](../COMPARISON-SUMMARY.md).
2. Open `tables/02-remaining-19.csv` for the current unresolved findings.
3. Look at `figures/01-overall-status.png`, `figures/02-priority-status.png`, and `figures/03-old-vs-new-half-half.png`.
4. Use `tables/01-all-86-findings.csv` when you need the complete searchable list.
5. Open `proof/08-executed-comparison-notebook.ipynb` to inspect the August 12 checks.

## Figure provenance and scope

| File | Use | Provenance or limit |
|---|---|---|
| `figures/01-overall-status.png` | Counts of fixed, remaining, and changed findings. | Generated for this August 12 package from the 86-row status table. |
| `figures/02-priority-status.png` | P1 and P2/P3 breakdown. | Generated for this package; priorities come from the August 10 audit. |
| `figures/03-old-vs-new-half-half.png` | Side-by-side view of the saved raw two-condition overlays. | Generated for this package from saved evidence; it does not test the composed output dimensions in `PV-BUG-034`. |
| `figures/04-old-compound-coordinate-bug.png` | Small controlled image from the old bug reproduction. | Copied from the August 10 evidence folder. |
| `figures/05-new-gene-and-compound.png` | Example v3 gene-and-compound rendering. | Copied from the August 11 v3 results. |
| `figures/06-old-svg-missing-edges.svg` | Old SVG edge-rendering evidence. | Copied from the August 10 evidence folder. |
| `figures/07-new-svg-with-edges.svg` | v3 SVG containing pathway edge paths. | Copied from the August 11 v3 results. |
| `figures/08-new-working-highlights.png` | v3 highlight operation example. | Copied from the August 11 v3 results; label conversion has a separate remaining finding. |
| `figures/09-new-namespaced-sbgn.svg` | v3 namespace-aware SBGN example. | Copied from the August 11 SBGN results; it is not a live Reactome route test. |
| `figures/10-new-graph-mode-current-output.png` | Current graph-mode example. | Copied from the August 11 v3 results; the multi-condition first-color issue remains. |

## Tables

- `tables/01-all-86-findings.csv`: one row for every August 10 finding and its v3 status.
- `tables/02-remaining-19.csv`: the 19 rows still reproduced by the v3 recheck.
- `tables/03-fixed-60.csv`: the 60 rows classified as fixed under the narrow audit rule.
- `tables/04-changed-7.csv`: the seven rows whose old contract was replaced.
- `tables/05-comparison-summary.json`: counts, priorities, versions, commits, and test totals.

## Proof files

- `proof/01-august-10-bug-list.json` and `proof/02-august-10-test-summary.json` are the original August 10 source data.
- `proof/03-august-10-environment.json` records the old audit environment.
- `proof/04-august-10-executed-notebook.ipynb` is the original executed audit notebook.
- `proof/05-v3-status-source.json` is the complete v3 classification mapping saved from the August 11 evidence.
- `proof/06-v3-final-test-summary.txt` and `proof/07-v3-final-junit.xml` are the saved final v3 upstream test results.
- `proof/08-executed-comparison-notebook.ipynb` and `proof/09-notebook-execution-proof.json` document the August 12 package checks.
