# Use PyGAGE from the command line

*Page 24 of 31*

The command-line interface lets you run PyGAGE 1.2.1 from Terminal without
writing a Python script.

PyGAGE installs one command with four subcommands:

```text
pygage run
pygage kegg
pygage go
pygage compare
```

## Before typing a command

Open Terminal, move into the project folder, and activate the virtual
environment created on page 2.

macOS or Linux:

```bash
cd my-pygage-project
source .venv/bin/activate
```

Windows PowerShell:

```powershell
cd my-pygage-project
.venv\Scripts\Activate.ps1
```

Confirm the installed package version:

```bash
python -c "import pygage; print(pygage.__version__)"
```

This guide uses:

```text
1.2.1
```

Create the folders used by the examples:

```bash
python -c "from pathlib import Path; Path('gene_sets').mkdir(exist_ok=True); Path('results').mkdir(exist_ok=True); Path('pygage_cache/kegg').mkdir(parents=True, exist_ok=True)"
```

## Ask PyGAGE for help

Show the four subcommands:

```bash
pygage --help
```

Show every option for one subcommand:

```bash
pygage run --help
pygage kegg --help
pygage go --help
pygage compare --help
```

Add `-v` or `--verbose` before the subcommand to print progress messages:

```bash
pygage --verbose run expression.csv \
  --gene-sets gene_sets.json \
  --output results.csv \
  --ref 0,1 \
  --samp 2,3
```

## Command-line file rules

Use these beginner-safe formats:

| Purpose | Recommended filename | How PyGAGE reads or writes it |
| --- | --- | --- |
| expression or DE input | `.csv` | comma-separated |
| expression or DE input | `.tsv` | tab-separated |
| gene sets | `.json` | plain mapping or top-level `gene_sets` |
| compressed gene sets | `.json.gz` | gzip-compressed JSON |
| gene sets | `.gmt` | tab-separated GMT |
| result output | `.csv` | comma-separated |
| result output | `.tsv` | tab-separated |
| GO annotation | `.gaf` | local GAF 2.x text |
| GO ontology | `.obo` | local OBO text |

For command-line GMT input, use an uncompressed `.gmt` file. Direct Python
loaders additionally support gzip-compressed GMT files.

## Subcommand 1: `pygage run`

Use `run` for an expression matrix, prepared matrix, or differential-expression
table.

Basic shape:

```bash
pygage run INPUT \
  --gene-sets GENE_SET_FILE \
  --output RESULT_FILE
```

The positional `INPUT`, `--gene-sets`, and `--output` are required.

### Every `run` option

| Option | Default | Meaning |
| --- | --- | --- |
| `INPUT` | required | expression matrix or DE table |
| `-g FILE`, `--gene-sets FILE` | required | GMT or JSON gene-set file |
| `-o FILE`, `--output FILE` | required | result CSV or TSV |
| `--de-table` | off | treat input as DESeq2, edgeR, or limma output |
| `--value {log2FC,stat}` | `log2FC` | choose the DE value used for ranking |
| `--ref TEXT` | none | comma-separated 0-based reference indices |
| `--samp TEXT` | all non-reference columns when `--ref` is set | comma-separated 0-based sample indices |
| `--compare {paired,unpaired,as.group,1ongroup}` | `paired` | prepare raw sample comparisons |
| `--prepared` | off | input numeric columns are already changes or statistics |
| `--test {t-test,z-test,ks-test}` | `t-test` | per-set statistical test |
| `--meta {stouffer,fisher}` | `stouffer` | combine evidence across columns |
| `--one-direction` | off | use `same_dir=False`; raw preparation uses absolute changes |
| `--min-size INTEGER` | `10` | minimum matched genes in a tested set |
| `--max-size INTEGER` | `500` | maximum matched genes in a tested set |
| `--top INTEGER` | `15` | number of result rows printed in Terminal |

The gene-ID column is not counted by `--ref` or `--samp`.

For this table:

```text
gene_id | control_1 | control_2 | treated_1 | treated_2
```

the value-column indices are:

```text
control_1 = 0
control_2 = 1
treated_1 = 2
treated_2 = 3
```

### Raw paired matrix

```bash
pygage run expression.csv \
  --gene-sets gene_sets/kegg_hsa_entrez.json \
  --output results/kegg_paired.csv \
  --ref 0,1 \
  --samp 2,3 \
  --compare paired \
  --test t-test \
  --meta stouffer
```

Use `paired` when each sample column is matched to a reference column.

### Raw unpaired matrix

```bash
pygage run expression.csv \
  --gene-sets gene_sets/kegg_hsa_entrez.json \
  --output results/kegg_unpaired.csv \
  --ref 0,1,2 \
  --samp 3,4,5 \
  --compare unpaired
```

Use `unpaired` for unmatched groups.

### Group-average comparison

```bash
pygage run expression.csv \
  --gene-sets gene_sets/kegg_hsa_entrez.json \
  --output results/kegg_group_average.csv \
  --ref 0,1,2 \
  --samp 3,4,5 \
  --compare as.group
```

`as.group` calculates one mean sample-versus-reference comparison.

### One sample against the reference group

```bash
pygage run expression.csv \
  --gene-sets gene_sets/kegg_hsa_entrez.json \
  --output results/kegg_one_on_group.csv \
  --ref 0,1,2 \
  --samp 3,4,5 \
  --compare 1ongroup
```

`1ongroup` compares each sample with the mean of the reference group.

### Already prepared values

For a table shaped like:

```text
gene_id	change_1	change_2
7157	1.8	2.1
672	-1.2	-1.0
```

run:

```bash
pygage run prepared.tsv \
  --gene-sets gene_sets/kegg_hsa_entrez.json \
  --output results/prepared_results.csv \
  --prepared
```

### DESeq2, edgeR, or limma table

Use log2 fold change:

```bash
pygage run deseq2_results.csv \
  --gene-sets gene_sets/kegg_hsa_entrez.json \
  --output results/deseq2_log2fc.csv \
  --de-table \
  --value log2FC
```

Use a statistical-score column:

```bash
pygage run deseq2_results.csv \
  --gene-sets gene_sets/kegg_hsa_entrez.json \
  --output results/deseq2_stat.csv \
  --de-table \
  --value stat
```

PyGAGE recognizes common gene, fold-change, and statistic column names. Page 12
shows how to handle custom column names in Python.

## Subcommand 2: `pygage kegg`

Use `kegg` to download pathway, KO, or module gene sets.

Basic shape:

```bash
pygage kegg {pathway,ko,module} --output FILE
```

### Every `kegg` option

| Option | Default | Meaning |
| --- | --- | --- |
| `{pathway,ko,module}` | required | kind of KEGG gene set |
| `-o FILE`, `--output FILE` | required | destination JSON file |
| `-s CODE`, `--species CODE` | `hsa` | KEGG organism code for pathway/module |
| `--reference {pathway,module}` | `pathway` | reference grouping for KO sets |
| `--id-type {kegg,entrez}` | `entrez` | member-ID type for organism pathways |
| `--cache DIRECTORY` | none | local KEGG response cache |

### Organism-specific pathways

```bash
pygage kegg pathway \
  --output gene_sets/kegg_hsa_entrez.json \
  --species hsa \
  --id-type entrez \
  --cache pygage_cache/kegg
```

The JSON contains `gene_sets`, `set_names`, and `categories`.

### Species-independent KO pathways

```bash
pygage kegg ko \
  --output gene_sets/ko_pathways.json \
  --reference pathway \
  --cache pygage_cache/kegg
```

The KO JSON also contains a KO catalog and provenance record.

### Species-independent KO modules

```bash
pygage kegg ko \
  --output gene_sets/ko_modules.json \
  --reference module \
  --cache pygage_cache/kegg
```

### Organism-specific modules

```bash
pygage kegg module \
  --output gene_sets/hsa_modules.json \
  --species hsa \
  --cache pygage_cache/kegg
```

The module JSON contains `gene_sets` and `set_names`.

The first KEGG download uses the internet. With `--cache`, later matching
requests can reuse the local text responses. The final JSON can be reused
directly by `pygage run`.

## Subcommand 3: `pygage go`

Use `go` to build gene sets from a local GAF annotation file.

Basic shape:

```bash
pygage go ANNOTATIONS.gaf --output GO_SETS.json
```

### Every `go` option

| Option | Default | Meaning |
| --- | --- | --- |
| `GAF` | required | local GAF 2.x annotation file |
| `-o FILE`, `--output FILE` | required | destination JSON file |
| `--obo FILE` | none | optional OBO file for names and propagation |
| `--aspect {BP,MF,CC}` | all | restrict to one GO domain |
| `--id-field {symbol,object_id}` | `symbol` | choose the GAF gene-ID field |
| `--no-iea` | off | exclude IEA electronic annotations |
| `--propagate` | off | add annotations to OBO parent terms |

Build propagated Biological Process sets:

```bash
pygage go reference_files/annotations.gaf \
  --output gene_sets/go_bp.json \
  --obo reference_files/go-basic.obo \
  --aspect BP \
  --id-field symbol \
  --propagate
```

Exclude IEA annotations:

```bash
pygage go reference_files/annotations.gaf \
  --output gene_sets/go_bp_without_iea.json \
  --obo reference_files/go-basic.obo \
  --aspect BP \
  --id-field symbol \
  --no-iea \
  --propagate
```

This command reads local files and writes `gene_sets` plus collection
`metadata` to JSON.

## Subcommand 4: `pygage compare`

Use `compare` to place result tables from several conditions side by side.

Basic shape:

```bash
pygage compare RESULT_1 RESULT_2 \
  --output COMBINED_FILE
```

### Every `compare` option

| Option | Default | Meaning |
| --- | --- | --- |
| `RESULTS...` | one or more required | CSV or TSV PyGAGE result files |
| `-o FILE`, `--output FILE` | required | combined CSV or TSV |
| `--names TEXT` | input filename stems | comma-separated condition names |
| `--q-cutoff NUMBER` | `0.1` | threshold used to count significant-condition hits |
| `--top INTEGER` | `15` | rows printed in Terminal |

Example:

```bash
pygage compare \
  results/control.csv \
  results/treatment_a.csv \
  results/treatment_b.csv \
  --output results/combined_conditions.tsv \
  --names Control,Treatment_A,Treatment_B \
  --q-cutoff 0.1 \
  --top 20
```

Supply one name for every result file, in the same order.

The combined table can contain:

- `<name>_stat` columns;
- `<name>_q` or `<name>_p` columns; and
- `hits`, the number of conditions passing the chosen cutoff.

## Save a reproducibility record

The output table does not replace the command that created it. Save a plain
text file named `analysis_command.txt` containing:

```text
PyGAGE version: 1.2.1
Input: expression.csv
Gene sets: gene_sets/kegg_hsa_entrez.json
Reference columns: 0,1,2
Sample columns: 3,4,5
Comparison: unpaired
Test: t-test
Meta method: stouffer
Set-size range: 10,500
Command:
pygage run expression.csv --gene-sets gene_sets/kegg_hsa_entrez.json --output results.csv --ref 0,1,2 --samp 3,4,5 --compare unpaired
```

Also keep the gene-set metadata or KEGG provenance beside this record.

## Final command-line checklist

- the virtual environment is active;
- PyGAGE reports version `1.2.1`;
- every input filename and output filename is different;
- CSV files use commas and TSV/GMT files use tabs;
- expression IDs match the gene-set IDs;
- raw-matrix indices exclude the gene-ID column;
- the species, reference type, and ID type are recorded;
- downloaded reference data and caches are retained; and
- the exact command is saved with the results.

[<- Previous: Make enrichment plots](23-visualization.md) | [Home](index.md) | [Next: Use a Jupyter notebook ->](25-notebooks.md)
