# Cite PyGAGE and get support

*Page 31 of 31*

Use this page when preparing a methods section, sharing an analysis, reporting
the software version, reviewing the license, or asking a project question.

## Cite the PyGAGE article

The preferred citation recorded in PyGAGE 1.2.1's `CITATION.cff` is:

> Figueroa III JL, Brouwer CR, White III RA. 2026. *Statistically resolving
> gene-set enrichment for pathway analysis that is broadly applicable via
> PyGAGE.* bioRxiv.

Copyable plain text:

```text
Figueroa III JL, Brouwer CR, White III RA. 2026. Statistically resolving gene-set enrichment for pathway analysis that is broadly applicable via PyGAGE. bioRxiv.
```

The citation metadata does not currently list an article DOI. Use the project
record above together with the exact PyGAGE version and source repository.

## Cite the original GAGE method

PyGAGE implements the GAGE method. Cite the original GAGE article as well:

> Luo W, Friedman MS, Shedden K, Hankenson KD, Woolf PJ. 2009. GAGE:
> generally applicable gene set enrichment for pathway analysis. *BMC
> Bioinformatics* 10:161.
> [https://doi.org/10.1186/1471-2105-10-161](https://doi.org/10.1186/1471-2105-10-161)

Copyable plain text:

```text
Luo W, Friedman MS, Shedden K, Hankenson KD, Woolf PJ. 2009. GAGE: generally applicable gene set enrichment for pathway analysis. BMC Bioinformatics 10:161. https://doi.org/10.1186/1471-2105-10-161
```

## Cite the gene-set sources

Also cite and report the biological resources used to create the gene sets,
such as KEGG, Gene Ontology, Reactome, or MSigDB.

For every collection, record:

- database or collection name;
- organism or KO reference;
- release or version;
- retrieval date;
- identifier system;
- collection filename;
- set count; and
- checksum when available.

Use the citation guidance distributed by each database for its exact
publication references.

## Suggested methods text

Adapt this template to the analysis:

> Gene-set enrichment was performed with PyGAGE 1.2.1 using the t-test
> gene-set statistic, Stouffer cross-sample combination, a matched set-size
> range of 10–500 genes, and Benjamini-Hochberg adjustment. Separate greater
> and less directions were evaluated. Gene sets were obtained from [source,
> release, organism, retrieval date] and used [identifier system]. Sets with
> [recorded q-value rule] were selected for downstream interpretation.

Replace every bracketed section with the real analysis information. If a
setting differs from the standard configuration, state the chosen value.

## License

PyGAGE is distributed under the Creative Commons
Attribution-NonCommercial 4.0 license:

```text
CC BY-NC 4.0
```

The repository license permits use, copying, modification, and distribution
for academic, research, and noncommercial purposes when the copyright and
permission notice are retained.

Commercial use requires prior written permission from the copyright holder.
Commercial licensing questions may be directed to:

```text
Richard Allen White III
rwhit101@charlotte.edu
```

Read the complete license text in the official repository:

[PyGAGE LICENSE](https://github.com/raw-lab/pygage/blob/main/LICENSE)

## Official project links

- Source repository:
  [https://github.com/raw-lab/pygage](https://github.com/raw-lab/pygage)
- Questions and issue reports:
  [https://github.com/raw-lab/pygage/issues](https://github.com/raw-lab/pygage/issues)
- Documentation project:
  [https://pygage.readthedocs.io](https://pygage.readthedocs.io)
- Package record:
  [https://pypi.org/project/PyGAGE/](https://pypi.org/project/PyGAGE/)

Primary project contact:

```text
Dr. Richard Allen White III
rwhit101@charlotte.edu
```

## Report the exact PyGAGE version

Run:

```bash
python -c "import pygage; print(pygage.__version__)"
```

This guide is based on:

```text
PyGAGE 1.2.1
source commit 486e0b800778ec03fe03764aa9dccbe904cfd70b
```

If the repository is inside `my-pygage-project/pygage`, record its selected
commit with:

```bash
git -C pygage rev-parse HEAD
```

## Create a complete software version report

Inside `my-pygage-project`, create `make_version_report.py`:

```python
import platform
import sys
from importlib.metadata import (
    PackageNotFoundError,
    version,
)
from pathlib import Path

import pygage


package_names = [
    "polars",
    "numpy",
    "scipy",
    "matplotlib",
    "seaborn",
    "pandas",
    "pyarrow",
    "requests",
]

lines = [
    f"PyGAGE: {pygage.__version__}",
    f"Python: {sys.version.split()[0]}",
    f"Operating system: {platform.platform()}",
]

for package_name in package_names:
    try:
        installed_version = version(package_name)
    except PackageNotFoundError:
        installed_version = "not installed"
    lines.append(
        f"{package_name}: {installed_version}"
    )

report = "\n".join(lines) + "\n"

Path("version_report.txt").write_text(
    report,
    encoding="utf-8",
)

print(report)
print("Saved version_report.txt")
```

Run:

```bash
python make_version_report.py
```

This creates:

```text
version_report.txt
```

Keep the file beside the final results and analysis code.

## Complete reproducibility checklist

### Software

- PyGAGE version;
- source commit when installed from GitHub;
- Python version;
- operating system;
- relevant package versions;
- command-line or Python API route; and
- script or notebook.

### Measurement input

- input filename;
- input type: raw, prepared, differential-expression, pre-ranked, pandas, or
  AnnData;
- table dimensions;
- gene identifier system;
- preprocessing and normalization;
- meaning of positive and negative values;
- reference samples;
- comparison samples; and
- comparison design.

### Gene sets

- source;
- release;
- retrieval date;
- organism or KO reference;
- identifier system;
- file or cache key;
- number of sets; and
- checksum.

### Analysis settings

- set-size range;
- test method;
- meta-method;
- separate or magnitude-only direction handling;
- FDR method;
- control gene set when used;
- global or per-direction BH setting;
- effect calculation;
- leading-edge setting;
- permutation count;
- random seed;
- worker count; and
- thread environment.

### Result handling

- complete result table;
- direction;
- filtering rule;
- selected result table;
- grouping or redundancy settings;
- comparison names;
- plot settings; and
- final tables and figures.

## Ask a clear project question

GitHub Issues is useful when a question could help other PyGAGE users:

[Open the PyGAGE issue page](https://github.com/raw-lab/pygage/issues)

Include:

1. a short descriptive title;
2. PyGAGE and Python versions;
3. operating system;
4. function or command used;
5. input type and identifier system;
6. analysis settings;
7. a small reproducible example when possible;
8. the complete Terminal or Python message; and
9. what result you expected.

Before attaching a file, remove participant information, credentials, private
paths, and other sensitive material.

## Final project checklist

A well-recorded PyGAGE project contains:

```text
project/
├── data/
├── gene_sets/
├── results/
├── figures/
├── analysis.py
├── analysis_notebook.ipynb
├── version_report.txt
└── README.md
```

The project README should summarize the biological comparison, identifier
system, gene-set source, main settings, filtering rule, citations, and the
order in which scripts or notebook cells should be run.

[<- Previous: Complete Python API](30-api-reference.md) | [Home](index.md) | [Next: Return to the beginning ->](01-before-you-begin.md)
