# Pathview Plus comparison notes — August 12, 2026

This folder is my written record of the follow-up to the Pathview Plus bug audit from August 10. I compared the old audited snapshot with the v3.1.0 snapshot and carried the same finding IDs forward so that each old result has one clearly stated current status.

The comparison covers Pathview Plus only. It does not include PyGAGE, R Pathview, or SBGNview as separate software comparisons.

## Result in one paragraph

There were 86 unique findings in the August 10 audit. At Pathview Plus 3.1.0, 60 of the old failure conditions were absent under the audit rules, 19 could still be demonstrated with an adapted check or current source path, and 7 could not receive a fixed/broken verdict because the relevant API or workflow had been replaced. All 86 IDs were accounted for exactly once. The original priority split was 14 fixed, 5 still reproducible, and 1 changed among 20 P1 findings; the remaining 66 P2/P3 findings were split 46 fixed, 14 still reproducible, and 6 changed.

The remaining P1 IDs are `PV-BUG-006`, `PV-BUG-034`, `PV-BUG-038`, `PV-BUG-074`, and `PV-BUG-075`. They concern unmapped rows, composed native image dimensions, multi-condition graph colors, the Reactome route, and replacement of an Entrez label with a gene symbol.

## What the status words mean

The status is attached to the old finding, not to the whole Pathview Plus project.

- **Fixed:** the original August 10 failure condition was absent in a current v3 test, an adapted version of the old check, or a direct review of the current code path.
- **Still reproducible:** a v3-equivalent check still showed the underlying behavior. A partial improvement does not erase the remaining part of the finding.
- **Changed interface/behavior:** the old argument, CLI branch, or dispatch route was removed or replaced. That old reproducer is no longer a fair test of the new contract, so it is listed separately rather than called fixed.

The priorities were inherited from August 10. P1 means the original audit connected the finding to a main workflow or advertised feature. P2/P3 covers smaller validation issues, API boundaries, and edge cases. The priorities were not recalculated for v3.

## Exact snapshots

| Snapshot | Package/version information | Commit |
|---|---|---|
| August 10 audited snapshot | distribution `2.0.2`; runtime `pathview.__version__` was `2.0.0` | `07aee813375347bcc933ad21b4aed561dd7cd3bf` |
| v3 snapshot | distribution and runtime `3.1.0` | `d4d45decec56e1ebec15cf04ae62ff944851780e` |

The old commit is the code from the `v2.0.2` tag with a later README change. The v3 commit is its immediate next commit. The GitHub comparison records 88 changed files, with 21,134 insertions and 10,325 deletions.

This handoff is dated August 12. The v3 test result and status JSON were saved from the August 11 source checkout; those original dates remain visible in the copied proof files so that the evidence is traceable.

## How to read the test counts

The August 10 audit had 239 test cases: 143 ordinary passes, 89 known-bug reproductions, 7 feature-gap reproductions, and 0 unexplained failures. Those cases produced 79 unique reproduced bugs plus 7 unique feature gaps, or 86 unique findings.

The v3 upstream suite is a different suite. It collected 327 tests, passed 321, skipped 6, and failed 0 in the saved final run. Those numbers are supporting context; they are not a before-and-after pass-rate comparison. The comparable denominator is the same 86 old finding IDs.

## Where to begin

1. Read [`COMPARISON-SUMMARY.md`](COMPARISON-SUMMARY.md) for the method, result, limitations, and next steps.
2. Open [`reports/REMAINING-19.md`](reports/REMAINING-19.md) to see the current behavior for every unresolved finding.
3. Open [`reports/ALL-86-FINDINGS.md`](reports/ALL-86-FINDINGS.md) for the complete index.
4. Use [`outputs-that-matter/00-START-HERE.md`](outputs-that-matter/00-START-HERE.md) to find the selected figures, tables, and proof files.
5. Open the [executed notebook](notebooks/executed/01-old-vs-new-pathview-bug-comparison.executed.ipynb) if you want to see the checks that were run for the August 12 comparison package.

## What was actually done for this folder

The August 12 work assembled and checked the saved evidence. It verified the joins, counts, commit IDs, pathway-file hashes, saved image dimensions, JUnit totals, CSV row counts, local links, and notebook outputs. It did not rerun every old bug test from scratch. The original August 10 audit and the v3 upstream run are preserved as proof files, and no Pathview Plus source code was modified while preparing this folder.

## Rebuilding the package

The commands below assume the existing sibling evidence folders and the existing v3 virtual environment are still present. This folder is therefore a documented comparison package, not a standalone software distribution.

```bash
MPLCONFIGDIR="$PWD/08-12-2026/.mplconfig" \
  08-11-2026/.venv/bin/python 08-12-2026/scripts/build_comparison.py

MPLCONFIGDIR="$PWD/08-12-2026/.mplconfig" \
  08-11-2026/.venv/bin/python 08-12-2026/scripts/build_and_run_notebook.py
```

The data and comparison scripts use frozen local evidence. They do not contact KEGG, Reactome, PANTHER, or SMPDB.
