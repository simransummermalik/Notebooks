# Paper update notes — August 13, 2026

I read the current paper draft and compared it with the new files in this
folder. I am not copying the draft into this repository. These are my notes on
what changed and what I think needs to be added.

## What the draft already covers

The draft already explains the basic reason for Pathview Plus, the Python
workflow, input tables, identifier mapping, output formats, and three examples:

- a gene-expression example on human KEGG pathway `hsa04151`;
- a three-condition example on `hsa04010`; and
- a MetaCerberus/KO example on `ko00910`.

That material can stay as the introduction and use-case part of the paper. The
examples should continue to be described as software demonstrations, not as
new biological discoveries.

## What changed since the older Pathview Plus version in the draft

The draft was written around an older snapshot of the software. The current
comparison is based on Pathview Plus 3.1.0. The new files add a separate
source-level comparison with R Pathview 1.47.1 and R SBGNview 1.5.1.

The new comparison tracks 74 capabilities. It reports 73 as full for
Pathview Plus and one as not applicable because a Python package cannot import
the R Bioconductor OrgDb package itself. For the comparable features, the
reported coverage is 32/33 against Pathview R and 53/54 against SBGNview R.
The API tables show 22/22 applicable Pathview exports and 13/13 applicable
SBGNview exports. The argument table shows 24/25 Pathview arguments and 19/19
SBGNview arguments covered.

This is different from the August 10–12 bug follow-up. The earlier work tracks
86 old bug and feature IDs. The August 13 files track 74 capabilities and API
items. The two counts should not be added together or presented as one score.

## Sections I think need to be added

### 1. A short software-version paragraph

Add the current software versions and explain that the paper’s original
description was based on an earlier snapshot. Give the Pathview Plus version,
the two R comparison versions, and the date on which the source comparison was
made. If commit IDs are available in the final checkout, include them in the
methods or supplement.

### 2. A comparison-methods subsection

Explain exactly what was measured:

- R exports were read from `NAMESPACE`;
- R function arguments were read from the `R/*.R` source files;
- package versions were read from `DESCRIPTION`; and
- the Python side was inspected from the exported API and feature matrix.

The subsection needs one clear limitation sentence: R was not executed for
this comparison. Therefore the results show source/API coverage, not matching
runtime behavior, speed, memory use, or pixel-by-pixel image equality.

### 3. A feature-parity result

Add the 74-feature result and one compact table or figure. Figure 1 is the best
overview because it shows the categories and the three package totals. Figure
4 is useful for the statement that 11 tracked capabilities are present in
Pathview Plus but not in either R package.

### 4. API and argument coverage

Add Figure 2 for exported functions and Figure 3 for the arguments of the main
`pathview()` and `SBGNview()` entry points. The text should explain that names
were matched even when R and Python use different names, such as
`kegg.native` and `render_mode`.

### Where I would place the new material

I would leave the current workflow figure as Figure 1. I would use the
feature-parity image as the next main figure, then use the API and argument
images either as a second multi-panel figure or as supplementary figures. The
capability-overlap image is useful for the results paragraph but does not need
to be a separate main-text figure if space is limited.

The new comparison fits best after the existing workflow and output-format
sections and before the use cases. That order lets the paper explain the
software first, describe how the comparison was done, and then show the three
examples.

### 5. A better limitations paragraph

The paper should not say that the new Python package is identical to either R
package based only on these files. A fair statement is that the source review
found broad API and capability coverage, while runtime equivalence still needs
the same pathway and data rendered by both implementations.

### 6. Updated availability information

Update the implementation/availability section with the current repository and
documentation links. The repository link is:

`https://github.com/raw-lab/pathview-plus`

The package metadata also lists the documentation site as:

`https://pathview-plus.readthedocs.io`

The GitHub repository is the RAW Lab `pathview-plus` repository, so that is the
link I would use in the paper rather than a personal fork.

### 7. Replace the unfinished figure and table placeholders

The draft still has a placeholder for a comparison figure and another figure
that is not defined yet. I would replace those with the saved August 13
figures, give each one a real caption, and either complete or remove the cost
comparison table. A cost table should only be included if there are actual
measurements with the same input and hardware; the current source comparison
does not provide that.

### 8. Add citations and a reproducibility note

The final paper still needs the running bibliography. At minimum, cite the R
Pathview and R SBGNview packages, the pathway databases used in the examples,
MetaCerberus for the KO example, and the Pathview Plus repository. The
reproducibility note should point readers to the CSV files, `summary.json`,
comparison script, and the archived source package.

## What I would keep out of the main paper

I would not place all 154 combined CSV rows or all 74 feature descriptions in
the main text. Put the full tables in supplementary material or the repository,
then show the summary figures and explain how the counts were made.

I would also keep the August 10–12 bug list as a separate validation record.
It is useful evidence for the repository, but it would make the paper’s main
comparison difficult to follow if it were mixed into the feature-parity result.

## My lab-notebook conclusion

The new files look usable for a paper update. They add the comparison that the
older draft was missing, and the figures are readable. Before I treat the
numbers as final, I would correct the old R-version text in the archived
`parity.py` docstring, keep the source-based limitation visible, add the real
figure captions, and update the availability and references sections.
