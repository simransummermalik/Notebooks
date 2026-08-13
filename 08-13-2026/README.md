# August 13, 2026: new comparison files

This folder contains the new comparison material added for the paper. I checked
the files before using them as paper evidence.

## What is in this folder

The `files/` folder contains:

- `compare_r_packages.py`, the script that makes the comparison;
- `pathview-plus.tar.gz`, a copy of the Pathview Plus 3.1.0 source package;
- four CSV files containing the API, argument, feature, and combined tables;
- `summary.json`, the numbers used for the figures; and
- four PNG figures showing feature parity, API coverage, argument coverage,
  and where capabilities overlap.

The archive reports Pathview Plus 3.1.0. The comparison tables identify the R
packages as Pathview 1.47.1 and SBGNview 1.5.1.

## Checks I made

The four figures open normally and have usable image sizes. The tables contain
74 feature rows, 36 exported-symbol rows, 44 argument rows, and 154 combined
rows. The summary agrees with those tables:

- 73 of 74 tracked capabilities are marked full for Pathview Plus;
- one capability is marked not applicable (the R Bioconductor OrgDb package
  itself);
- the API table reports 22/22 applicable Pathview exports and 13/13
  applicable SBGNview exports;
- the argument table reports 24/25 Pathview arguments covered and 19/19
  SBGNview arguments covered; and
- the feature matrix reports 32/33 comparable Pathview features and 53/54
  comparable SBGNview features.

The numbers came from the source files. The script reads R `NAMESPACE`,
`DESCRIPTION`, and `R/*.R` files, then checks the installed Python package. I
did not run the R packages here, compare running times, or test pixel-for-pixel
identity. I would state that clearly in the paper.

## Two small documentation issues to fix later

1. The comparison script originally called the fourth output
   `fig4_capability_venn.png`, but the actual file is
   `fig4_capability_split.png`. I corrected the script’s output list.
2. The archived `lib/parity.py` docstring still mentions older R versions
   (1.46 and 1.20), while the saved comparison tables report 1.47.1 and
   1.5.1. The paper should use the versions in `summary.json`, and the
   archived source docstring should be corrected when the source package is
   updated.

The original audit folders from August 10–12 are still separate. I am not
combining their 86 historical bug statuses with this 74-feature parity table.
They answer different questions.
