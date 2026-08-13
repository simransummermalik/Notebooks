# R vs Python — what I got

I ran the new Pathview Plus against R Pathview and R SBGNview using the same
files and data. Here is what matched and what did not.

## R Pathview vs Pathview Plus

| What I checked | R Pathview | Python Pathview Plus | Result |
|---|---|---|---|
| Shared KEGG genes | Used 5/5 IDs | Used 5/5 IDs | Matched |
| One, two, and three conditions | Colored all three cases | Colored all three cases | Matched |
| Two-condition order | Control left, Treatment right | Control left, Treatment right | Matched |
| Raw pathway size | 1039 x 801 | 1039 x 801 | Matched |
| Genes and compounds together | Both data types mapped | Both data types mapped | Matched |
| KEGG mapping rows | 5 rows | 8 repeated/grouped rows for the same 5 IDs | Different |
| C00022 compound circle | 8-pixel radius | 4-pixel radius | Different |

The shared KEGG images were about **90.16% identical by pixel**, with an
average channel difference of **1.39 out of 255**. They are very close, but
they are not the exact same image.

## R SBGNview vs Pathview Plus

| What I checked | R SBGNview | Python Pathview Plus | Result |
|---|---|---|---|
| Shared genes | Used 7/7 symbols | Used 7/7 symbols | Matched |
| Pathway structure | 78 glyphs and 83 arcs | 76 main glyphs + 2 compartments and 83 arcs | Matched total |
| Two-condition order | Control left, Treatment right | Control left, Treatment right | Matched |
| Direct gene matches | 9 glyphs | 9 glyphs | Matched |
| Extra SLC18A2 mapping | Added 3 VAT1-labeled glyphs | Did not add the 3 VAT1 glyphs | Different |
| State and clone marks | Kept and drew them | Kept the data but did not draw the marks | Different |
| Output files | Wrote PNG and SVG | Wrote PNG and SVG | Matched |

Basically, the main workflows worked and the new Python version is much closer
to R. The clearest differences are the compound size, repeated/grouped KEGG
rows, the SLC18A2/VAT1 mapping, and drawing the SBGN state and clone marks.

## Test totals

| Test group | Passed | Failed | Skipped |
|---|---:|---:|---:|
| Pathview Plus test suite | 321 | 0 | 6 |
| My Python comparison checks | 16 | 0 | 0 |
| My R Pathview checks | 10 | 1 comparison difference | 0 |
| R/Python SBGN checks | 17 | 0 | 0 |

The one R comparison difference is the compound-circle size above. R still
finished the test without crashing.

## What changed from August 10

I rechecked all 86 findings from my August 10 work:

- 60 are fixed.
- 19 still happen.
- 7 are handled differently in the new version.
- 0 were left unchecked.

The five bigger things still left from that list are `map_null`, the size of
the normal composed image, graph-mode coloring with multiple conditions, the
Reactome download route, and replacing nonblank symbol labels. The full list
is in [`reports/V3-CHANGE-AUDIT.md`](reports/V3-CHANGE-AUDIT.md).

## Two smaller things I noticed

- A spreadsheet with a completely blank row and an unmatched ID can cause a
  mixed `str`/`None` sorting error. `data.drop_nulls()` avoids it for now.
- The repository README links to a missing `BUG_CHECKLIST.md`. It also says 21
  bugs were fixed while the changelog says 18.

## What I would check next

1. Make the SLC18A2/VAT1 mapping match R if that is the goal.
2. Draw the SBGN state and clone marks that Python already reads.
3. Decide which compound-size rule Pathview Plus should use.
4. Automatically remove completely blank input rows.
5. Go through the five bigger August 10 items still left.

## Version I tested

- Pathview Plus 3.1.0, commit `d4d45decec56e1ebec15cf04ae62ff944851780e`
- R Pathview 1.52.0
- R SBGNview 1.26.0

My overall answer is that the new version did the main things I tested and
fixed most of what I found yesterday. It still does not match R in every small
detail, but now the differences are specific and easy to test again.
