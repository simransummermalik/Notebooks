# Use Pathview Plus from the command line

*Page 18 of 24*

Use this page when you want to make a pathway directly from Terminal or
PowerShell. The command-line interface, or **CLI**, provides Pathview Plus
settings as named command options.

Python scripts remain useful when you need custom table preparation or a long
reproducible workflow. The CLI is convenient when your input is already a
simple TSV file.

## 1. Activate the project environment

First complete [Install Pathview Plus](02-install.md).

On macOS or Linux:

```bash
cd my-pathview-project
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
cd my-pathview-project
.\.venv\Scripts\Activate.ps1
```

## 2. Create the reusable CLI launcher

Keep `pathview_setup.py` from page 3 in the project folder. Create one more
file named `pathview_cli.py` beside it:

```python
import runpy
import sys
from pathlib import Path

from pathview_setup import prepare_pathview


prepare_pathview()

installed_cli = Path(sys.executable).parent / "pathview-cli.py"
runpy.run_path(installed_cli, run_name="__main__")
```

This small launcher runs the installed Pathview Plus command-line program
after applying the same Pathview Plus 2.0.2 setup used throughout the guide.
Create it once. Every command on this page starts with:

```text
python pathview_cli.py
```

Your project now contains:

```text
my-pathview-project/
├── .venv/
├── pathview_setup.py
└── pathview_cli.py
```

## 3. Check the command

Type:

```bash
python pathview_cli.py --help
```

The help page lists every option and several examples. It begins with:

```text
usage: pathview ...
Overlay gene/compound data on KEGG pathway diagrams.
```

The `--help` option prints the reference and then exits.

## 4. Prepare a gene TSV file

Create `gene_data.tsv` inside `my-pathview-project`:

```tsv
entrez_id	log2_fold_change
7157	-1.8
1956	2.4
3845	1.1
5290	1.5
207	0.9
```

The first column contains IDs. Every later column contains numeric values.
The same table shape is explained on
[Prepare your own data](04-prepare-your-data.md).

For several conditions, add more numeric columns:

```tsv
entrez_id	Control	Treatment_A	Treatment_B
1956	0.5	2.1	1.8
2099	-0.3	-1.5	-0.9
5594	1.2	0.4	2.3
```

## 5. Make an output folder

Type:

```bash
mkdir pathview_output
```

You only need to create this folder once.

## 6. Run a normal gene-data command

Type this as one line:

```bash
python pathview_cli.py --pathway-id 04151 --species hsa --gene-data gene_data.tsv --gene-idtype ENTREZ --kegg-dir pathview_output --out-suffix cli_first --no-map-symbol --kegg-native --output-format png
```

The command means:

| Part | Meaning |
| --- | --- |
| `python pathview_cli.py` | run the Pathview Plus CLI |
| `--pathway-id 04151` | choose PI3K-Akt signaling |
| `--species hsa` | choose human |
| `--gene-data gene_data.tsv` | load the gene table |
| `--gene-idtype ENTREZ` | read the first column as Entrez IDs |
| `--kegg-dir pathview_output` | save pathway files in this folder |
| `--out-suffix cli_first` | place `cli_first` in the finished filename |
| `--no-map-symbol` | keep direct identifier-based pathway labels |
| `--kegg-native` | use the KEGG pathway picture |
| `--output-format png` | write a PNG |

The finished image is:

```text
pathview_output/hsa04151.cli_first.png
```

The CLI also reports how many input rows and experiment columns were loaded
and how many pathway nodes were mapped.

The complete option reference below also lists the CLI's compound-table
settings. For the complete compound-only and gene-plus-compound tutorials, use
[Map compounds and multi-omics data](09-compounds-and-multiomics.md).

## Make simulated practice data

The CLI can create a simulated gene table internally:

```bash
python pathview_cli.py --simulate --n-sim 500 --pathway-id 04151 --species hsa --kegg-dir pathview_output --out-suffix simulated_cli --no-map-symbol --kegg-native --output-format png
```

| Option | Job |
| --- | --- |
| `--simulate` | use simulated gene measurements instead of a TSV |
| `--n-sim 500` | generate 500 molecule rows |
| `--pathway-id 04151` | choose the pathway to draw |

The finished file is:

```text
pathview_output/hsa04151.simulated_cli.png
```

Simulation is useful for learning and demonstrations. Page 17 explains
simulation settings in Python.

## Display the KEGG element legend

Type:

```bash
python pathview_cli.py --legend
```

This displays the reference legend for KEGG pathway nodes and edges, then
exits. A pathway ID and data table are not needed for this command.

## Make SVG or PDF output

Use the recommended format pairs from
[Choose PNG, SVG, or PDF output](15-output-formats.md).

For SVG:

```bash
python pathview_cli.py --pathway-id 04151 --species hsa --gene-data gene_data.tsv --gene-idtype ENTREZ --kegg-dir pathview_output --out-suffix cli_vector --no-map-symbol --no-kegg-native --output-format svg
```

For PDF:

```bash
python pathview_cli.py --pathway-id 04151 --species hsa --gene-data gene_data.tsv --gene-idtype ENTREZ --kegg-dir pathview_output --out-suffix cli_graph --no-map-symbol --no-kegg-native --output-format pdf
```

These commands create:

```text
pathview_output/hsa04151.cli_vector.svg
pathview_output/hsa04151.cli_graph.pdf
```

## Complete option reference

### Pathway and help

| Option | Default | Meaning |
| --- | --- | --- |
| `-h`, `--help` | off | print the complete command help and exit |
| `--pathway-id PATHWAY_ID` | required for a pathway run | KEGG number such as `04151`, or prefixed ID such as `hsa04151` |

`--pathway-id` is not required when `--legend` is used by itself.

### Input data

| Option | Default | Meaning |
| --- | --- | --- |
| `--gene-data TSV` | none | gene TSV; first column is IDs and later columns are numeric measurements |
| `--cpd-data TSV` | none | compound TSV; first column is IDs and later columns are numeric measurements |
| `--gene-idtype TYPE` | `ENTREZ` | gene ID type: `ENTREZ`, `SYMBOL`, `UNIPROT`, `ENSEMBL`, or `KEGG` |
| `--cpd-idtype TYPE` | `KEGG` | compound ID type: `KEGG`, `PUBCHEM`, or `CHEBI` |

A normal pathway run needs at least one gene table, compound table, or the
`--simulate` option.

### Species, folders, and names

| Option | Default | Meaning |
| --- | --- | --- |
| `--species SPECIES` | `hsa` | KEGG species code |
| `--kegg-dir DIR` | current folder, `.` | folder for downloaded pathway files and finished images |
| `--out-suffix OUT_SUFFIX` | `pathview` | text placed before the finished file extension |

### Rendering

| Option | Default | Meaning |
| --- | --- | --- |
| `--kegg-native` | on | use the KEGG PNG background for native PNG output |
| `--no-kegg-native` | off | choose the vector or graph route |
| `--output-format {png,pdf,svg}` | `png` | request PNG, PDF, or SVG output |
| `--map-symbol` | on | request gene-symbol labels |
| `--no-map-symbol` | off | keep direct identifier-based pathway labels |
| `--node-sum {sum,mean,median,max,max_abs,random}` | `sum` | combine repeated values that map to one node |
| `--min-nnodes MIN_NNODES` | `3` | minimum number of pathway nodes available for mapping |
| `--no-signature` | off | omit the rendering signature |
| `--no-col-key` | off | omit the numeric color-scale key |

Because the signature and color key are on by default, add their `--no-...`
options only when you want to omit them.

### Gene color scale

| Option | Default | Meaning |
| --- | --- | --- |
| `--limit-gene LIMIT_GENE` | `1.0` | symmetric gene limit from negative to positive |
| `--bins-gene BINS_GENE` | `10` | number of gene color bins |
| `--low-gene LOW_GENE` | `green` | low-end gene color |
| `--mid-gene MID_GENE` | `gray` | middle gene color |
| `--high-gene HIGH_GENE` | `red` | high-end gene color |

For example:

```text
--limit-gene 2.5 --bins-gene 10 --low-gene blue --mid-gene white --high-gene red
```

This makes a symmetric gene scale from `-2.5` to `2.5`.

### Compound color scale

| Option | Default | Meaning |
| --- | --- | --- |
| `--limit-cpd LIMIT_CPD` | `1.0` | symmetric compound limit from negative to positive |
| `--bins-cpd BINS_CPD` | `10` | number of compound color bins |
| `--low-cpd LOW_CPD` | `blue` | low-end compound color |
| `--mid-cpd MID_CPD` | `gray` | middle compound color |
| `--high-cpd HIGH_CPD` | `yellow` | high-end compound color |

### Utilities

| Option | Default | Meaning |
| --- | --- | --- |
| `--legend` | off | display the KEGG element legend and exit |
| `--simulate` | off | generate and use simulated gene data |
| `--n-sim N_SIM` | `200` | number of simulated molecules used with `--simulate` |

## Build a longer command clearly

On macOS or Linux, a backslash lets one command continue on the next line:

```bash
python pathview_cli.py \
  --pathway-id 04151 \
  --species hsa \
  --gene-data gene_data.tsv \
  --gene-idtype ENTREZ \
  --kegg-dir pathview_output \
  --out-suffix treatment_vs_control \
  --no-map-symbol \
  --kegg-native \
  --output-format png \
  --limit-gene 2.5 \
  --low-gene blue \
  --mid-gene white \
  --high-gene red
```

On Windows PowerShell, use a backtick at the end of each continued line:

```powershell
python pathview_cli.py `
  --pathway-id 04151 `
  --species hsa `
  --gene-data gene_data.tsv `
  --gene-idtype ENTREZ `
  --kegg-dir pathview_output `
  --out-suffix treatment_vs_control `
  --no-map-symbol `
  --kegg-native `
  --output-format png `
  --limit-gene 2.5 `
  --low-gene blue `
  --mid-gene white `
  --high-gene red
```

## CLI record to save

Save these items with a completed command-line analysis:

- the exact command;
- the input TSV file or simulation settings;
- the Pathview Plus version;
- pathway ID and species code;
- identifier type;
- output suffix and format;
- summary method;
- color limits and color names; and
- finished image and downloaded pathway files.

[<- Previous: Simulate and summarize data](17-simulate-and-summarize.md) | [Home](index.md) | [Next: Use KEGG tools ->](19-kegg-tools.md)
