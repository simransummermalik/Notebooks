# Use a differential-expression table

*Page 12 of 31*

Use this route when DESeq2, edgeR, limma, or another method has already
calculated one value per gene. PyGAGE 1.2.1 can select a log2 fold change or a
statistical score from the table.

## Example input

Create `de_results.csv`:

```csv
gene_id,log2FoldChange,stat,pvalue,padj
1,2.4,5.2,0.0001,0.001
2,2.0,4.7,0.0002,0.002
3,1.8,4.2,0.0004,0.003
4,1.5,3.7,0.0010,0.006
5,-0.2,-0.4,0.6800,0.790
6,0.1,0.2,0.8400,0.900
7,-1.8,-4.1,0.0005,0.004
8,-2.1,-4.8,0.0002,0.002
9,-1.5,-3.5,0.0014,0.008
10,-1.2,-3.0,0.0030,0.015
11,0.3,0.6,0.5500,0.680
12,-0.1,-0.2,0.8400,0.900
```

## Complete log2-fold-change workflow

Create `run_de_table.py`:

```python
import json
from pathlib import Path

import polars as pl
from pygage import gage, read_de_table


gene_sets = json.loads(
    Path("gene_sets.json").read_text()
)

de_values = read_de_table(
    source="de_results.csv",
    gene_col="gene_id",
    value="log2FC",
    stat_col=None,
    lfc_col="log2FoldChange",
)

results = gage(
    data=de_values,
    gene_sets=gene_sets,
    gene_col="gene_id",
    prepared=True,
    set_size_range=(2, 10),
)

significant = results.filter(
    pl.col("q_val") < 0.05
)

de_values.write_csv("selected_de_values.csv")
results.write_csv("de_enrichment_results.csv")
significant.write_csv(
    "de_significant_results.csv"
)

print("Input passed to GAGE:")
print(de_values)
print("Enrichment results:")
print(results)
```

Run:

```bash
python run_de_table.py
```

`selected_de_values.csv` contains only:

```text
gene_id | log2FC
```

The DE program's `pvalue` and `padj` columns remain part of the original file;
PyGAGE uses the chosen gene-level value for enrichment.

## Exact `read_de_table()` signature

```python
read_de_table(
    source,
    gene_col=None,
    value="log2FC",
    stat_col=None,
    lfc_col=None,
)
```

It returns a two-column Polars DataFrame.

| Argument | Default | Meaning |
| --- | --- | --- |
| `source` | required | CSV/TSV path or table |
| `gene_col` | `None` | auto-detect the gene column |
| `value` | `"log2FC"` | choose `"log2FC"` or `"stat"` |
| `stat_col` | `None` | auto-detect the statistical-score column |
| `lfc_col` | `None` | auto-detect the log2-fold-change column |

The reader recognizes common names such as:

- genes: `gene`, `gene_id`, `id`, `symbol`, `feature`, `ensembl`;
- fold change: `log2FoldChange`, `log2FC`, `logFC`, `lfc`, `coef`; and
- statistic: `stat`, `t`, `statistic`, `wald`, `z`, `lr`.

Explicit column names, as used in the script, make a reusable workflow clear.

Rows with a missing selected gene ID or selected numeric value are removed.
Gene IDs become text and the selected values become floating-point numbers.

## Analyze the statistical score instead

Replace the reader call with:

```python
de_values = read_de_table(
    "de_results.csv",
    gene_col="gene_id",
    value="stat",
    stat_col="stat",
)
```

The returned columns are:

```text
gene_id | stat
```

Choose log2 fold change when enrichment should reflect change magnitude.
Choose the statistical score when enrichment should reflect the gene-level
test statistic. Record the choice with the results.

## Why no reference indices are needed

Each DE row already summarizes a comparison. There are no control and treatment
sample columns left to subtract:

```text
raw samples -> differential-expression method -> one value per gene
```

`prepared=True` tells the high-level workflow to send that value directly to
the enrichment engine.

[<- Previous: Run the staged workflow](11-staged-analysis.md) | [Home](index.md) | [Next: Use pre-ranked data ->](13-preranked.md)
