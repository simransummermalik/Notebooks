# Filter, group, compare, and export

*Page 22 of 31*

Use this page after PyGAGE has produced result tables. It covers the steps that
turn a long enrichment result into a smaller, traceable collection of
pathways and genes:

```text
complete result
      |
      +--> filter by a recorded rule
      |
      +--> group overlapping gene sets
      |
      +--> compare conditions
      |
      +--> extract and export member genes
```

Keep the complete unfiltered result. Every smaller table should be something
you can recreate from it.

## 1. Filter a result

When you have the dictionary returned by `GAGEAnalysis.run_gage()`:

```python
from pygage.results_analysis import SignificanceFilter


filtered = SignificanceFilter.filter_significant(
    tables,
    cutoff=0.05,
    use_q=True,
    dual_sig=2,
)

greater_significant = filtered["greater"]
less_significant = filtered["less"]
```

This example:

- filters `q_val`, because `use_q=True`;
- uses a cutoff of `0.05`; and
- keeps both rows if a set passes in both directions, because `dual_sig=2`.

Page 21 explains all three `dual_sig` rules.

## 2. Understand why gene sets overlap

Biological processes share genes. Two pathway names can therefore appear as
separate significant results even when much of their signal comes from the
same measured genes.

Grouping does not erase the original result. It creates a summary that helps
you inspect related hits together.

PyGAGE offers two grouping approaches:

| Tool | What defines a connection? | Best use |
| --- | --- | --- |
| `GeneSetGrouper.group_gene_sets()` | statistically strong membership overlap among significant sets | organize sets by shared measured members |
| `esset_grp()` | overlap among direction-specific core genes, evaluated against essential genes | reproduce the GAGE-style redundancy workflow |

## 3. Group by measured membership

This workflow tests whether significant gene sets overlap more than expected
within the measured-gene universe.

```python
from pathlib import Path

from pygage.results_analysis import GeneSetGrouper


groups = GeneSetGrouper.group_gene_sets(
    results=tables["greater"],
    gene_sets=gene_sets,
    expression_data=prepared_data,
    gene_col="gene_id",
    p_cutoff=0.01,
    overlap_cutoff=1e-10,
    output_file=Path("greater_overlap_groups.json"),
)

print(groups)
```

The saved JSON has a structure like:

```json
{
  "Group_1": [
    "Pathway A",
    "Pathway B"
  ],
  "Group_2": [
    "Pathway C"
  ]
}
```

Important inputs are:

| Input | Meaning |
| --- | --- |
| `results` | one directional PyGAGE result table |
| `gene_sets` | the same gene-set dictionary used in enrichment |
| `expression_data` | the prepared table defining the measured universe |
| `p_cutoff` | result p-value rule used before grouping |
| `overlap_cutoff` | hypergeometric overlap p-value rule |

If fewer than two sets pass the result cutoff, there is nothing to group and
the returned dictionary is empty.

## 4. Run GAGE-style essential-set grouping

`esset_grp()` first identifies core genes for each significant set and
essential genes in the measured data. It then groups sets with strongly
overlapping core genes.

```python
from pygage.results_analysis import esset_grp


summary = esset_grp(
    results=tables["greater"],
    expression_data=prepared_data,
    gene_sets=gene_sets,
    gene_col="gene_id",
    test4up=True,
    same_dir=True,
    cutoff=0.01,
    use_q=False,
    pc=1e-10,
)

print("Groups:")
print(summary["groups"])

print("Core genes by set:")
print(summary["core_genes"])

print("Essential genes:")
print(summary["essential_genes"])

print("Number of essential genes:")
print(summary["n_essential"])
```

For a `less` result, use:

```python
summary = esset_grp(
    results=tables["less"],
    expression_data=prepared_data,
    gene_sets=gene_sets,
    test4up=False,
    same_dir=True,
)
```

The default selection follows the GAGE-style p-value workflow. If the analysis
plan uses q-values for this step, set:

```python
use_q=True
```

## 5. Compare two or more conditions

First save one directional result file for each condition:

```python
condition_a_tables["greater"].write_csv(
    "condition_a_greater.csv"
)
condition_b_tables["greater"].write_csv(
    "condition_b_greater.csv"
)
```

Then create one joined comparison:

```python
from pathlib import Path

from pygage.results_analysis import ResultsComparator


comparison = ResultsComparator.compare_results(
    result_files=[
        Path("condition_a_greater.csv"),
        Path("condition_b_greater.csv"),
    ],
    sample_names=[
        "condition_a",
        "condition_b",
    ],
    q_cutoff=0.05,
    output_file=Path("condition_comparison.csv"),
)

print(
    comparison.select(
        [
            "gene_set",
            "condition_a_stat",
            "condition_a_q",
            "condition_b_stat",
            "condition_b_q",
            "hits",
        ]
    )
)
```

`hits` counts how many supplied conditions pass the cutoff for that gene set.
The original condition-specific statistics and q-values stay in separate
columns.

Use short names made from letters, numbers, and underscores. They become parts
of the output column names.

## 6. Make a two- or three-condition Venn diagram

Using the same result files:

```python
ResultsComparator.create_venn_comparison(
    result_files=[
        Path("condition_a_greater.csv"),
        Path("condition_b_greater.csv"),
    ],
    sample_names=[
        "condition_a",
        "condition_b",
    ],
    q_cutoff=0.05,
    output_file=Path("condition_venn.png"),
)
```

The figure shows how many gene sets pass the rule in condition A only,
condition B only, both, or neither.

For three conditions, provide exactly three files and three names:

```python
ResultsComparator.create_venn_comparison(
    result_files=[
        Path("condition_a_greater.csv"),
        Path("condition_b_greater.csv"),
        Path("condition_c_greater.csv"),
    ],
    sample_names=[
        "condition_a",
        "condition_b",
        "condition_c",
    ],
    q_cutoff=0.05,
    output_file=Path("three_condition_venn.png"),
)
```

Venn diagrams are designed for two or three conditions. The joined comparison
table can be used for a larger number.

## 7. Count Venn regions from a membership table

Use `VennDiagram` directly when you already have a zero/nonzero membership
table:

```python
from pathlib import Path

import polars as pl
from pygage.visualization_utils import VennDiagram


membership = pl.DataFrame(
    {
        "condition_a": [1, 1, 0, 1, 0],
        "condition_b": [1, 0, 1, 1, 0],
    }
)

counts = VennDiagram.venn_counts(
    membership,
    include="both",
)

print(counts)

VennDiagram.plot_venn2(
    counts,
    names=["condition_a", "condition_b"],
    output_file=Path("membership_venn.png"),
)
```

The `include` setting can be:

| Value | Counts a row when |
| --- | --- |
| `"both"` | its value is nonzero |
| `"up"` | its value is positive |
| `"down"` | its value is negative |

`VennDiagram.plot_venn3()` uses the same pattern for a three-column membership
table.

## 8. Extract strongly changing members of one set

Choose a gene set from the result and pass its member list:

```python
from pygage.data_processing_utils import GeneExtractor


selected_name = "Growth pathway"

essential_genes = GeneExtractor.extract_essential_genes(
    gene_set=gene_sets[selected_name],
    expression_data=prepared_data,
    gene_col="gene_id",
    threshold=1.0,
    rank_by_abs=True,
)

print(essential_genes)
```

PyGAGE calculates each gene's mean prepared value, standardizes it against the
measured-gene distribution, and retains genes whose absolute standardized
value is above `threshold`.

`rank_by_abs=True` places the strongest positive or negative deviations first.

## 9. Export selected genes and a heatmap

```python
from pathlib import Path

from pygage.data_processing_utils import GeneDataExporter


selected_ids = essential_genes["gene_id"].to_list()

GeneDataExporter.export_gene_data(
    genes=selected_ids,
    expression_data=prepared_data,
    gene_col="gene_id",
    output_file=Path("selected_genes.csv"),
    create_heatmap=True,
    heatmap_output=Path("selected_genes_heatmap.png"),
    normalize=True,
)
```

This creates:

```text
selected_genes.csv
selected_genes_heatmap.png
```

With `normalize=True`, every gene row is converted to row-wise z scores for
the heatmap. The exported table keeps the original supplied values.

## 10. Normalize a table directly

```python
from pygage.data_processing_utils import DataTransformer


row_scaled = DataTransformer.row_normalize(
    prepared_data,
    gene_col="gene_id",
)

column_scaled = DataTransformer.column_normalize(
    prepared_data,
    gene_col="gene_id",
)
```

The two operations answer different visualization questions:

| Operation | What is standardized? | Common interpretation |
| --- | --- | --- |
| `row_normalize()` | each gene across its columns | relative pattern for each gene |
| `column_normalize()` | each column across genes | relative gene values within each column |

These are transformation utilities. Do not silently replace the values used
for enrichment; save transformed data under a new variable name.

## 11. Prepare paired differences with the utility class

The main preparation route is described on Page 8. The data-processing utility
also provides a paired or unpaired difference helper:

```python
from pygage.data_processing_utils import DataTransformer


paired_changes = DataTransformer.prepare_paired_data(
    data=raw_expression,
    ref_indices=[0, 1],
    samp_indices=[2, 3],
    gene_col="gene_id",
    comparison="paired",
    use_fold=True,
    input_logged=True,
    log_base=2.0,
    pseudocount=1.0,
)
```

Indices count only the numeric columns, beginning at zero. With two references
and two samples, this produces two matched sample-minus-reference columns.
Use `comparison="unpaired"` to create every sample/reference combination.

## 12. Make a reference-versus-sample scatterplot

Use raw expression columns, not the already subtracted comparison:

```python
from pathlib import Path

from pygage.data_processing_utils import GeneDataExporter


GeneDataExporter.create_scatterplot(
    expression_data=raw_expression,
    ref_col="control_1",
    samp_col="treated_1",
    gene_col="gene_id",
    genes=None,
    output_file=Path("control_vs_treated.png"),
    title="Control 1 versus treated 1",
)
```

Supply a list through `genes=` to draw only selected members.

## Final checklist

- the filter rule is written down;
- grouping uses the same gene sets and measured universe as enrichment;
- each comparison uses the same direction and analysis settings;
- condition names match the saved files;
- extracted IDs match the expression-table identifier system; and
- the complete result stays beside every filtered or grouped summary.

[<- Previous: Use advanced analysis options](21-advanced-options.md) | [Home](index.md) | [Next: Make enrichment plots ->](23-visualization.md)
