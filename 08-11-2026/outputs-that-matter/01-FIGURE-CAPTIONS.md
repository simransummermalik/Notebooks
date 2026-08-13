# Ready-to-use figure captions

## Figure 1 — Main R pathview versus Python Pathview Plus comparison

Side-by-side rendering of the human Cell Cycle pathway (`hsa04110`) using R pathview 1.52.0 (left) and Python Pathview Plus 3.1.0 (right). Both programs received the same frozen KEGG pathway files and the same Control/Treatment gene data. The first condition is shown on the left half of each mapped node and the second condition is shown on the right.

File: `01-key-figures/01-r-pathview-vs-python-pathview-cell-cycle.png`

## Figure 2 — Half-and-half CDKN2A control

Close-up of the controlled CDKN2A node used to verify two-condition orientation. The negative first condition appears green on the left, and the positive second condition appears red on the right. Separate Python and R close-ups are provided.

Files:

- `01-key-figures/05-python-pathview-half-and-half-CDKN2A-closeup.png`
- `01-key-figures/06-r-pathview-half-and-half-CDKN2A-closeup.png`

## Figure 3 — Three-condition Pathview output

Three-condition Pathview visualization showing three ordered color bands inside mapped nodes. The output confirms that Pathview Plus preserves the input-column order when more than two conditions are provided.

File: `01-key-figures/07-python-pathview-three-condition.png`

## Figure 4 — Gene and compound comparison

Controlled R pathview and Python Pathview Plus comparison using both gene and compound measurements on the same `hsa00020` pathway coordinates. Both programs mapped the shared molecular inputs; the figure also records the measured compound-size rendering variation.

File: `01-key-figures/09-r-vs-python-pathview-gene-and-compound.png`

## Figure 5 — Python Pathview Plus SBGN output

Python Pathview Plus rendering of the P00001 Adrenaline and Noradrenaline Biosynthesis SBGN pathway using the shared seven-gene Control/Treatment table. The two vertical halves represent the two input condition columns.

File: `01-key-figures/13-python-pathview-plus-sbgn-two-condition.png`

## Figure 6 — R SBGNview output

R SBGNview rendering of the same P00001 SBGN-ML pathway and shared seven-gene Control/Treatment table used for the Python comparison.

File: `01-key-figures/14-r-sbgnview-two-condition.png`

## Figure 7 — SBGN structural details

Small controlled SBGN pathway used to compare compartments, ports, state-variable data, clone-marker data, and arc connections in Python Pathview Plus and R SBGNview.

Files:

- `01-key-figures/17-python-sbgn-structural-details.svg`
- `01-key-figures/18-r-sbgnview-structural-details.svg`
