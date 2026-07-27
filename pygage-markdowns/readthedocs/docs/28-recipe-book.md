# Recipe book

*Page 28 of 31*

Use this page when you know the task you want to complete and need a direct
route to the correct page or a short, copyable PyGAGE example.

Each recipe is independent. Replace the example filenames with your own files
while keeping the shown table structures and identifier systems.

## Find the right recipe

| I want to | Recipe or full page |
| --- | --- |
| practice without downloading data | [Use the packaged real dataset](#run-the-packaged-offline-dataset) |
| analyze a genes-by-samples matrix | [Analyze a raw expression matrix](#analyze-a-raw-expression-matrix) |
| analyze prepared gene changes | [Analyze a prepared matrix](#analyze-a-prepared-matrix) |
| analyze DESeq2, edgeR, or limma output | [Analyze a differential-expression table](#analyze-a-differential-expression-table) |
| analyze one ranked score per gene | [Analyze a pre-ranked file](#analyze-a-pre-ranked-file) |
| use pandas | [Analyze a pandas DataFrame](#analyze-a-pandas-dataframe) |
| use an `.h5ad` file | [Analyze AnnData](#analyze-anndata) |
| convert symbols and Entrez IDs | [Convert gene identifiers](#convert-gene-identifiers) |
| download organism-specific KEGG pathways | [Get KEGG pathway sets](#get-kegg-pathway-sets) |
| analyze KO measurements | [Run a KO-level analysis](#run-a-ko-level-analysis) |
| build GO gene sets | [Build Gene Ontology sets](#build-gene-ontology-sets) |
| load a GMT or MSigDB collection | [Load a GMT collection](#load-a-gmt-collection) |
| load Reactome | [Load a Reactome collection](#load-a-reactome-collection) |
| save and reuse a gene-set collection | [Cache a collection](#cache-a-collection) |
| request advanced result columns | [Run the full engine](#run-the-full-engine) |
| filter and save results | [Filter a tidy result](#filter-a-tidy-result) |
| reduce redundant pathway results | [Group overlapping sets](22-group-overlap.md) |
| compare multiple result files | [Compare conditions](#compare-conditions) |
| make an enrichment figure | [Make a bubble plot](#make-a-bubble-plot) |
| choose t-test, z-test, KS, Stouffer, or Fisher | [Choose statistical settings](20-statistical-settings.md) |
| limit workers and threads | [Configure performance](27-performance.md) |
| use Terminal instead of Python code | [Open the CLI guide](24-command-line.md) |
| use notebook cells | [Open the notebook guide](25-notebooks.md) |
| look up every callable | [Open the API reference](30-api-reference.md) |
| cite PyGAGE and record versions | [Open citation and support](31-citation-and-support.md) |

## Run the packaged offline dataset

This recipe uses the real GSE16873 prepared matrix and KEGG sets included with
PyGAGE 1.2.1.

```python
import json
from pathlib import Path

import polars as pl
from pygage import core, gage


regression_folder = (
    Path(core.__file__).resolve().parent
    / "data"
    / "regression"
)

prepared = pl.read_csv(
    regression_folder / "gse16873_prepared.csv.gz",
    schema_overrides={"gene_id": pl.Utf8},
)

gene_sets = json.loads(
    (regression_folder / "kegg_gs.json").read_text(
        encoding="utf-8"
    )
)

result = gage(
    prepared,
    gene_sets,
    prepared=True,
)

print(
    result
    .filter(pl.col("direction") == "greater")
    .sort("p_val")
    .head(5)
)
```

Full explanation: [page 26](26-real-dataset.md).

## Analyze a raw expression matrix

This example expects:

```text
data/expression.csv
data/gene_sets.json
```

The expression table has `gene_id` first, followed by three reference columns
and three paired sample columns.

```python
import json
from pathlib import Path

from pygage import gage, read_matrix


expression = read_matrix(
    Path("data") / "expression.csv"
)

gene_sets = json.loads(
    (Path("data") / "gene_sets.json").read_text(
        encoding="utf-8"
    )
)

result = gage(
    expression,
    gene_sets,
    ref_indices=[0, 1, 2],
    samp_indices=[3, 4, 5],
    comparison="paired",
    input_logged=True,
)

output_folder = Path("results")
output_folder.mkdir(exist_ok=True)
result.write_csv(output_folder / "raw_matrix_results.csv")
```

The indices are zero-based positions among the numeric sample columns. The
`gene_id` column is not counted.

Full explanation: pages [6](06-expression-matrix.md),
[7](07-reference-and-sample.md), and [8](08-prepare-expression.md).

## Analyze a prepared matrix

This example expects a table whose numeric columns already represent
gene-level changes or statistics.

```python
import json
from pathlib import Path

import polars as pl
from pygage import gage, read_matrix


prepared = read_matrix(
    Path("data") / "prepared_matrix.csv"
)

gene_sets = json.loads(
    (Path("data") / "gene_sets.json").read_text(
        encoding="utf-8"
    )
)

result = gage(
    prepared,
    gene_sets,
    prepared=True,
)

selected = (
    result
    .filter(pl.col("q_val") < 0.05)
    .sort(["direction", "q_val"])
)

output_folder = Path("results")
output_folder.mkdir(exist_ok=True)
result.write_csv(output_folder / "prepared_all.csv")
selected.write_csv(output_folder / "prepared_selected.csv")
```

Full explanation: [page 10](10-one-call-gage.md).

## Analyze a differential-expression table

This example uses the log2-fold-change column from a DESeq2, edgeR, or limma
result table.

```python
import json
from pathlib import Path

from pygage import gage, read_de_table


de_table = read_de_table(
    Path("data") / "deseq2_results.csv",
    value="log2FC",
)

gene_sets = json.loads(
    (Path("data") / "gene_sets.json").read_text(
        encoding="utf-8"
    )
)

result = gage(
    de_table,
    gene_sets,
)

output_folder = Path("results")
output_folder.mkdir(exist_ok=True)
result.write_csv(output_folder / "de_enrichment.csv")
```

To rank by a detected test statistic, change `value="log2FC"` to
`value="stat"`.

Full explanation: [page 12](12-de-tables.md).

## Analyze a pre-ranked file

The input file has two columns:

```text
gene_id	score
7157	3.1
672	-2.4
1956	1.8
```

Use:

```python
import json
from pathlib import Path

from pygage import gage, read_preranked


ranked = read_preranked(
    Path("data") / "ranked_scores.tsv",
    gene_col="gene_id",
    score_col="score",
)

gene_sets = json.loads(
    (Path("data") / "gene_sets.json").read_text(
        encoding="utf-8"
    )
)

result = gage(
    ranked,
    gene_sets,
)

output_folder = Path("results")
output_folder.mkdir(exist_ok=True)
result.write_csv(output_folder / "ranked_enrichment.csv")
```

Full explanation: [page 13](13-preranked.md).

## Analyze a pandas DataFrame

This example reads a genes-by-samples CSV with pandas and uses three reference
and three sample columns.

```python
import json
from pathlib import Path

import pandas as pd
from pygage import gage


expression = pd.read_csv(
    Path("data") / "expression.csv"
)

gene_sets = json.loads(
    (Path("data") / "gene_sets.json").read_text(
        encoding="utf-8"
    )
)

result = gage(
    expression,
    gene_sets,
    ref_indices=[0, 1, 2],
    samp_indices=[3, 4, 5],
    gene_col="gene_id",
    comparison="paired",
)

output_folder = Path("results")
output_folder.mkdir(exist_ok=True)
result.write_csv(output_folder / "pandas_enrichment.csv")
```

PyGAGE converts the pandas table at the input boundary and returns a Polars
result table.

Full explanation: [page 14](14-pandas-anndata.md).

## Analyze AnnData

Install AnnData in the active environment:

```bash
python -m pip install anndata
```

Then use:

```python
import json
from pathlib import Path

import anndata as ad
from pygage import gage


adata = ad.read_h5ad(
    Path("data") / "expression.h5ad"
)

gene_sets = json.loads(
    (Path("data") / "gene_sets.json").read_text(
        encoding="utf-8"
    )
)

result = gage(
    adata,
    gene_sets,
    ref_indices=[0, 1, 2],
    samp_indices=[3, 4, 5],
    comparison="paired",
)

output_folder = Path("results")
output_folder.mkdir(exist_ok=True)
result.write_csv(output_folder / "anndata_enrichment.csv")
```

AnnData normally stores samples in observations and genes in variables.
PyGAGE transposes that matrix into genes by samples internally.

Full explanation: [page 14](14-pandas-anndata.md).

## Convert gene identifiers

PyGAGE includes a human Entrez-to-symbol mapping. This complete example
converts in both directions:

```python
from pygage.gene_id_utils import GeneIDConverter


converter = GeneIDConverter()

symbols = converter.eg2sym(
    ["7157", "672", "1956"],
)

entrez_ids = converter.sym2eg(
    ["TP53", "BRCA1", "EGFR"],
)

print("Symbols:", symbols)
print("Entrez IDs:", entrez_ids)
```

The output is:

```text
Symbols: ['TP53', 'BRCA1', 'EGFR']
Entrez IDs: ['7157', '672', '1956']
```

Run the conversion before enrichment when the measurement table and gene sets
use different identifier systems.

## Get KEGG pathway sets

This recipe contacts KEGG and retrieves human pathways with Entrez Gene IDs:

```python
import json
from pathlib import Path

from pygage.pathway_database_utils import (
    KEGGPathwayRetriever,
)


retriever = KEGGPathwayRetriever(
    cache_dir=Path("kegg_cache")
)

downloaded = retriever.get_pathway_genes(
    species="hsa",
    id_type="entrez",
)

payload = {
    "gene_sets": downloaded["gene_sets"],
    "pathway_names": downloaded["pathway_names"],
    "categories": downloaded["categories"],
}

Path("data").mkdir(exist_ok=True)
(Path("data") / "kegg_hsa.json").write_text(
    json.dumps(payload),
    encoding="utf-8",
)

print("Downloaded sets:", len(payload["gene_sets"]))
```

Full explanation: [page 15](15-kegg.md).

## Run a KO-level analysis

This recipe expects a prepared table with KO identifiers such as `K00844`.
The identifiers in the KO table and KO gene sets already use the same system.

```python
from pathlib import Path

from pygage import gage, read_matrix
from pygage.pathway_database_utils import (
    KEGGPathwayRetriever,
)


ko_data = read_matrix(
    Path("data") / "prepared_ko_matrix.csv",
    gene_col="gene_id",
)

retriever = KEGGPathwayRetriever(
    cache_dir=Path("kegg_cache")
)

downloaded = retriever.get_ko_gene_sets(
    reference="pathway"
)

result = gage(
    ko_data,
    downloaded["gene_sets"],
    prepared=True,
)

output_folder = Path("results")
output_folder.mkdir(exist_ok=True)
result.write_csv(output_folder / "ko_enrichment.csv")
```

Use `reference="module"` when the research question calls for KEGG modules.

Full explanation: [page 16](16-kegg-orthology.md).

## Build Gene Ontology sets

This recipe uses a GAF annotation file and `go-basic.obo`, keeps biological
process terms, includes IEA annotations, and propagates genes to ancestor
terms.

```python
from pathlib import Path

from pygage.gene_sets import load_go


go_collection = load_go(
    Path("data") / "goa_human.gaf",
    obo_path=Path("data") / "go-basic.obo",
    aspect="BP",
    id_field="symbol",
    include_iea=True,
    propagate=True,
)

print("GO sets:", go_collection.n_sets)
print("Metadata:", go_collection.metadata())
```

Pass `go_collection` directly to `gage()` when the measurement table also uses
gene symbols.

Full explanation: [page 17](17-gene-ontology.md).

## Load a GMT collection

This recipe loads a local MSigDB Hallmark file:

```python
from pathlib import Path

from pygage.gene_sets import load_msigdb


hallmark = load_msigdb(
    Path("data") / "h.all.v2023.2.Hs.symbols.gmt",
    collection="H",
)

print("Loaded sets:", hallmark.n_sets)
print("Metadata:", hallmark.metadata())
```

The measurement table must use the same gene identifiers as the GMT members.

Full explanation: [page 18](18-other-gene-sets.md).

## Load a Reactome collection

For a local Reactome GMT file:

```python
from pathlib import Path

from pygage.gene_sets import load_reactome


reactome = load_reactome(
    Path("data") / "ReactomePathways.gmt",
    id_type="gmt",
    species="Homo sapiens",
)

print("Reactome sets:", reactome.n_sets)
print("Metadata:", reactome.metadata())
```

Full explanation: [page 18](18-other-gene-sets.md).

## Cache a collection

This example saves a loaded collection and opens it again later:

```python
from pathlib import Path

from pygage.gene_sets import GeneSetCache, load_gmt


collection = load_gmt(
    Path("data") / "my_collection.gmt",
    source="Project gene sets",
    release="2026-07",
)

cache = GeneSetCache(
    cache_dir=Path("gene_set_cache")
)

saved_path = cache.save(
    "project_sets_2026_07",
    collection,
)

reloaded = cache.load(
    "project_sets_2026_07"
)

print("Saved cache:", saved_path)
print("Available keys:", cache.list_keys())
print("Reloaded sets:", reloaded.n_sets)
```

Full explanation: [page 18](18-other-gene-sets.md).

## Run the full engine

Use the staged API when the analysis needs explicit advanced controls:

```python
import json
from pathlib import Path

import polars as pl
from pygage import GAGEAnalysis, read_matrix


prepared = read_matrix(
    Path("data") / "prepared_matrix.csv"
)

gene_sets = json.loads(
    (Path("data") / "gene_sets.json").read_text(
        encoding="utf-8"
    )
)

analysis = GAGEAnalysis()

tables = analysis.run_gage(
    prepared,
    gene_sets,
    gene_col="gene_id",
    set_size_range=(10, 500),
    same_dir=True,
    test_method="t-test",
    meta_method="stouffer",
    fdr_method="BH",
    control_genes=None,
    global_bh=False,
    compute_effect=True,
    leading_edge=True,
    permutations=100,
    n_jobs=1,
    random_state=42,
)

greater = tables["greater"]
less = tables["less"]

print(
    greater.select(
        [
            "gene_set",
            "q_val",
            "effect",
            "leading_edge",
            "p_perm",
        ]
    ).head(10)
)

output_folder = Path("results")
output_folder.mkdir(exist_ok=True)
greater.write_csv(output_folder / "greater_advanced.csv")
less.write_csv(output_folder / "less_advanced.csv")
```

Full explanation: pages [20](20-statistical-settings.md) and
[21](21-advanced-options.md).

## Filter a tidy result

This recipe reads a saved tidy result, separates directions, applies a
recorded q-value rule, and saves the selected rows:

```python
from pathlib import Path

import polars as pl


result = pl.read_csv(
    Path("results") / "all_results.csv"
)

selected = (
    result
    .filter(pl.col("q_val") < 0.05)
    .sort(["direction", "q_val"])
)

greater = (
    selected
    .filter(pl.col("direction") == "greater")
)

less = (
    selected
    .filter(pl.col("direction") == "less")
)

selected.write_csv(
    Path("results") / "selected_results.csv"
)
greater.write_csv(
    Path("results") / "selected_greater.csv"
)
less.write_csv(
    Path("results") / "selected_less.csv"
)
```

Full explanation: [page 19](19-results.md).

## Compare conditions

This recipe combines two saved greater-direction result files. Each input
contains one row per gene set. The same pattern can be used for two
less-direction files.

```python
from pathlib import Path

from pygage.results_analysis import ResultsComparator


combined = ResultsComparator.compare_results(
    result_files=[
        Path("results") / "control_greater.csv",
        Path("results") / "treatment_greater.csv",
    ],
    sample_names=[
        "Control",
        "Treatment",
    ],
    q_cutoff=0.05,
    output_file=(
        Path("results") / "combined_conditions.csv"
    ),
)

print(combined.head(10))
```

The `hits` column counts how many supplied conditions pass the cutoff for each
gene set.

## Make a bubble plot

This complete example reads a tidy result file, selects the greater direction,
and saves a PNG:

```python
from pathlib import Path

import polars as pl
from pygage.visualization_utils import EnrichmentPlots


result = pl.read_csv(
    Path("results") / "all_results.csv"
)

greater = (
    result
    .filter(pl.col("direction") == "greater")
    .sort("q_val")
)

EnrichmentPlots.bubble_plot(
    greater,
    top_n=20,
    title="Greater-direction gene-set enrichment",
    output_file=Path("results") / "bubble_plot.png",
)
```

Full explanation: [page 23](23-visualization.md).

## Record the recipe used

For every completed analysis, save:

- input filename and input type;
- reference and sample definitions;
- meaning of positive and negative values;
- identifier system;
- gene-set source, release, and retrieval date;
- test, meta-method, set-size range, and direction setting;
- advanced options and random seed;
- filtering rule;
- PyGAGE version and source commit; and
- the script or notebook.

Page 31 provides a complete version-report script and citation text.

[<- Previous: Configure performance and threads](27-performance.md) | [Home](index.md) | [Next: Glossary ->](29-glossary.md)
