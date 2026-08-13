# Complete Python API reference

*Page 30 of 31*

This hand-organized reference covers the public Python API in PyGAGE 1.2.1 at
commit `486e0b8`. Types written as `DataFrame` are Polars DataFrames unless a
different library is named.

## Accepted core types

- `FrameLike`: Polars or pandas DataFrame, AnnData, or a column mapping.
- `PathLike`: string or operating-system path.
- `GeneSetMapping`: `{set_name: [gene_id, ...]}`.
- `GeneSetsLike`: a mapping or `GeneSetCollection`.
- Analysis input: `gene_id` plus one or more numeric value columns.
- Directional output: `gene_set`, `set_size`, `stat_mean`, `p_geomean`,
  `p_val`, `q_val`, optional extras, and—when tidy—`direction`.

See [input routes](05-choose-input.md), [gene sets](09-gene-sets.md), and
[results](19-results.md).

## High-level input and analysis

Import these from `pygage`.

```text
gage(data, gene_sets, ref_indices=None, samp_indices=None,
     gene_col="gene_id", comparison="paired", same_dir=True,
     test_method="t-test", meta_method="stouffer",
     set_size_range=(10, 500), input_logged=True,
     prepared=False, tidy=True, **run_kwargs)
```

Runs preparation plus enrichment. Returns one tidy DataFrame when `tidy=True`;
otherwise returns `{"greater", "less", "stats"}`. See [page 10](10-one-call-gage.md).

```text
read_matrix(source, gene_col="gene_id") -> DataFrame
```

Reads a genes-by-samples CSV/TSV or table and casts IDs to text.

```text
read_de_table(source, gene_col=None, value="log2FC",
              stat_col=None, lfc_col=None) -> DataFrame
```

Returns `gene_id` plus `log2FC` or `stat`. See [page 12](12-de-tables.md).

```text
read_preranked(source, gene_col="gene_id",
               score_col="score") -> DataFrame
```

Accepts a file, table, or `{gene: score}` mapping and returns `gene_id, score`.
See [page 13](13-preranked.md).

## Core engine

Imports:

```text
from pygage import (
    GAGEAnalysis, GAGEPreparation, GAGEResult,
    benjamini_hochberg,
)
```

```text
GAGEPreparation.prepare_expression(
    expression_data, ref_indices=None, samp_indices=None,
    gene_col="gene_id", comparison="paired", same_dir=True,
    use_fold=True, input_logged=True, rank_test=False,
) -> DataFrame
```

Creates paired, unpaired, `as.group`, or `1ongroup` gene-level comparisons.
See [page 8](08-prepare-expression.md).

```text
GAGEAnalysis() -> GAGEAnalysis
```

Creates an engine with `.results=None` and `.result_obj=None`.

```text
GAGEAnalysis.run_gage(
    expression_data, gene_sets, gene_col="gene_id",
    set_size_range=(10, 500), same_dir=True,
    test_method="t-test", meta_method="stouffer",
    fdr_method="BH", control_genes=None, global_bh=False,
    compute_effect=True, leading_edge=False, permutations=0,
    n_jobs=1, random_state=0,
) -> dict[str, DataFrame]
```

Returns `greater`, optional `less`, and `stats`. See
[staged analysis](11-staged-analysis.md), [settings](20-statistical-settings.md),
and [advanced options](21-advanced-options.md).

```text
GAGEAnalysis.filter_significant(cutoff=0.1,
                                use_q=True) -> dict[str, DataFrame]
```

Filters the stored directional results and retains `stats`.

```text
GAGEResult(greater, less, stats, meta={})
```

Typed result container.

```text
GAGEResult.as_dict() -> dict[str, DataFrame]
GAGEResult.significant(cutoff=0.1,
                       use_q=True) -> dict[str, DataFrame]
```

```text
benjamini_hochberg(pvals: numpy.ndarray) -> numpy.ndarray
```

Returns BH-adjusted values in input order while preserving NaNs.

## Gene-set collections and files

Import from `pygage.gene_sets`. In particular, import
`normalize_gene_sets` from this module, not the package top level.

```text
GeneSetCollection(gene_sets, source="unknown", release="unknown",
                  retrieved=<today>, n_sets=0, checksum="", extra={})
```

Dataclass carrying a gene-set mapping and provenance.

```text
GeneSetCollection.metadata() -> dict
GeneSetCollection.as_dict() -> dict[str, list[str]]
GeneSetCollection.filter_size(lo=5, hi=1000) -> GeneSetCollection
normalize_gene_sets(gene_sets) -> dict[str, list[str]]
```

`normalize_gene_sets()` stringifies names/IDs and de-duplicates members in
order.

```text
load_gmt(path, source="GMT",
         release="unknown") -> GeneSetCollection
load_msigdb(path, collection="H") -> GeneSetCollection
load_reactome(path, id_type="gmt",
              species="Homo sapiens") -> GeneSetCollection
load_go(gaf_path, obo_path=None, aspect=None, id_field="symbol",
        include_iea=True, propagate=False) -> GeneSetCollection
```

These load GMT/MSigDB, Reactome, and GAF/OBO collections. See
[pages 17–18](18-other-gene-sets.md).

```text
GeneSetCache(cache_dir="~/.cache/pygage/gene_sets")
GeneSetCache.save(key, coll) -> pathlib.Path
GeneSetCache.load(key) -> GeneSetCollection | None
GeneSetCache.list_keys() -> list[str]
```

Stores and retrieves compressed, provenance-bearing collections.

## KEGG and Gene Ontology retrieval

Import from `pygage.pathway_database_utils`.

```text
KEGGPathwayRetriever(cache_dir=None, retries=3, pause=0.34)
```

Creates a KEGG REST retriever with optional disk cache and retry settings.

```text
KEGGPathwayRetriever.list_organisms() -> dict[str, str]
KEGGPathwayRetriever.get_species_code(species="hsa") -> dict[str, str]
KEGGPathwayRetriever.get_pathway_names(species="hsa") -> dict[str, str]
KEGGPathwayRetriever.get_pathway_genes(
    species="hsa", id_type="kegg") -> dict[str, object]
KEGGPathwayRetriever.get_ko_gene_sets(
    reference="pathway") -> dict[str, object]
KEGGPathwayRetriever.list_all_kos() -> dict[str, str]
KEGGPathwayRetriever.download_ko_gene_sets(
    output_file, reference="pathway",
    id_field="ko") -> dict[str, object]
KEGGPathwayRetriever.get_module_gene_sets(
    species="hsa") -> dict[str, object]
KEGGPathwayRetriever.categorize_pathways(
    pathway_ids) -> dict[str, list[str]]
```

Pathway/KO returns contain `gene_sets`, names, and categories as applicable.
The download method also writes JSON. See [KEGG](15-kegg.md) and
[KEGG Orthology](16-kegg-orthology.md).

```text
GOGeneSetRetriever()
GOGeneSetRetriever.get_go_gene_sets(
    annotation_file, id_field="symbol",
    include_iea=True, obo_file=None) -> dict[str, object]
```

Builds GO sets, names, and categories from a GAF and optional OBO.

## Gene-ID conversion

Import from `pygage.gene_id_utils`.

```text
GeneIDConverter(mapping_file=None)
GeneIDConverter.load_mapping(mapping_file) -> None
GeneIDConverter.eg2sym(entrez_ids,
                       as_frame=False) -> list[str | None] | DataFrame
GeneIDConverter.sym2eg(symbols,
                       as_frame=False) -> list[str | None] | DataFrame
build_kegg_symbol_map(species="hsa",
                      output_file=None) -> DataFrame
```

The converter accepts lists or Polars Series. `as_frame=True` returns
`input, output`; unmatched IDs return null. The builder can write TSV.

## Result analysis

Import from `pygage.results_analysis` (`esset_grp` is also exported by
`pygage`).

```text
esset_grp(results, expression_data, gene_sets, gene_col="gene_id",
          test4up=True, same_dir=True, cutoff=0.01,
          use_q=False, pc=1e-10) -> dict[str, object]
```

Returns redundant-set groups, core genes, and essential genes.

```text
ResultsComparator.compare_results(
    result_files, sample_names, q_cutoff=0.1,
    output_file=None) -> DataFrame
ResultsComparator.create_venn_comparison(
    result_files, sample_names, q_cutoff=0.1,
    output_file=None) -> None
GeneSetGrouper.group_gene_sets(
    results, gene_sets, expression_data, gene_col="gene_id",
    p_cutoff=0.01, overlap_cutoff=1e-10,
    output_file=None) -> dict[str, list[str]]
SignificanceFilter.filter_significant(
    results, cutoff=0.1, use_q=True,
    dual_sig=2) -> dict[str, DataFrame]
```

`dual_sig=0` excludes dual hits, `1` keeps the better direction, and `2` keeps
both. See [overlap and comparison](22-group-overlap.md).

## Data processing and export

Import from `pygage.data_processing_utils`.

```text
DataTransformer.row_normalize(data,
                              gene_col="gene_id") -> DataFrame
DataTransformer.column_normalize(data,
                                 gene_col="gene_id") -> DataFrame
DataTransformer.prepare_paired_data(
    data, ref_indices, samp_indices, gene_col="gene_id",
    comparison="paired", use_fold=True, input_logged=True,
    log_base=2.0, pseudocount=1.0) -> DataFrame
GeneExtractor.extract_essential_genes(
    gene_set, expression_data, gene_col="gene_id",
    threshold=1.0, rank_by_abs=False) -> DataFrame
GeneDataExporter.export_gene_data(
    genes, expression_data, gene_col="gene_id", output_file=None,
    create_heatmap=False, heatmap_output=None,
    normalize=True) -> None
GeneDataExporter.create_scatterplot(
    expression_data, ref_col, samp_col, gene_col="gene_id",
    genes=None, output_file=None, title=None) -> None
```

These normalize tables, create fold changes, select outlying set members, and
export selected data/figures.

## Visualization

Import from `pygage.visualization_utils`; `EnrichmentPlots` is also exported by
`pygage`. Plot methods save when `output_file` is supplied and otherwise show
the figure.

```text
ColorUtils.create_colormap(low, mid, high, n=256)
ColorUtils.greenred(n=256)
VennDiagram.venn_counts(data, include="both") -> DataFrame
VennDiagram.plot_venn2(counts, names, output_file=None,
                       figsize=(8, 8)) -> None
VennDiagram.plot_venn3(counts, names, output_file=None,
                       figsize=(10, 10)) -> None
HeatmapPlotter.plot_heatmap(
    data, row_labels=None, col_labels=None, cmap="RdYlGn_r",
    vmin=None, vmax=None, center=0, figsize=(10, 8),
    output_file=None, title=None, **kwargs) -> None
HeatmapPlotter.plot_clustered_heatmap(
    data, row_labels=None, col_labels=None, gene_col="gene_id",
    cmap="RdYlGn_r", vmin=None, vmax=None, figsize=(12, 10),
    output_file=None, title=None, **kwargs) -> None
EnrichmentPlots.bubble_plot(
    results, top_n=20, stat_col="stat_mean", q_col="q_val",
    size_col="set_size", name_col="gene_set",
    title="Enriched gene sets", output_file=None) -> None
EnrichmentPlots.enrichment_heatmap(
    results_by_condition, value="stat_mean", top_n=25,
    q_col="q_val", name_col="gene_set", output_file=None,
    title="Gene-set enrichment across conditions") -> None
EnrichmentPlots.running_enrichment(
    ranked, gene_set, gene_col="gene_id", score_col="score",
    weight=1.0, title=None, output_file=None) -> dict
EnrichmentPlots.pathway_gene_colors(
    pathway_genes, fold_changes, title="Pathway member fold changes",
    vmax=None, output_file=None) -> dict
```

See [visualization](23-visualization.md).

## Runtime configuration

Import `config` from `pygage`.

```text
config.packaged_data_dir() -> pathlib.Path
config.data_dir() -> pathlib.Path
config.resolve(name, explicit=None) -> pathlib.Path
config.egsymb_path(explicit=None) -> pathlib.Path
config.default_n_jobs() -> int
config.set_thread_limits(n_threads) -> None
config.thread_config() -> dict
config.ensure_egsymb(explicit=None, fetch=False,
                     species="hsa") -> pathlib.Path
```

Data resolution is explicit path, `PYGAGE_DATA_DIR`, then packaged data.
Compute controls are explained on [page 27](27-performance.md).

## Lower-level gene-set tests

Import from `pygage.tests`:

```text
GeneSetTests.t_test(
    expression_data, gene_sets, gene_col="gene_id",
    set_size_range=(10, 500),
    same_dir=True) -> dict[str, object]
GeneSetTests.z_test(
    expression_data, gene_sets, gene_col="gene_id",
    set_size_range=(10, 500),
    same_dir=True) -> dict[str, object]
GeneSetTests.kolmogorov_smirnov_test(
    expression_data, gene_sets, gene_col="gene_id",
    set_size_range=(10, 500),
    same_dir=True) -> dict[str, object]
```

Each returns `{"results": DataFrame, "method": ...}`. The result columns are
`gene_set`, `set_size`, `statistic`, `p_greater`, and `p_less`.

## Command line

The installed `pygage` program provides `run`, `kegg`, `go`, and `compare`.
See the complete option-by-option [command-line guide](24-command-line.md);
the Python and command-line interfaces use the same PyGAGE engine.

[<- Previous: Glossary](29-glossary.md) | [Home](index.md) | [Next: Cite, reproduce, and get support ->](31-citation-and-support.md)
