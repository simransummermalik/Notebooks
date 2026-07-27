# Complete API reference

*Page 23 of 24*

This page lists the public Python interface included with Pathview Plus 2.0.2.
Use it when you need to look up an argument, default value, return value, or
advanced helper.

Beginners can use the complete recipes earlier in the guide without memorizing
this page.

## Import the main function

```python
from pathview import pathview
```

The complete function signature is:

```python
pathview(
    pathway_id,
    gene_data=None,
    cpd_data=None,
    species="hsa",
    kegg_dir=".",
    kegg_native=True,
    output_format="png",
    gene_idtype="ENTREZ",
    cpd_idtype="KEGG",
    out_suffix="pathview",
    node_sum="sum",
    map_symbol=True,
    map_null=True,
    min_nnodes=3,
    new_signature=True,
    plot_col_key=True,
    limit=None,
    bins=None,
    both_dirs=None,
    discrete=None,
    low=None,
    mid=None,
    high=None,
    na_col="transparent",
    trans_fun=None,
    **kwargs,
)
```

At least one of `gene_data` or `cpd_data` is supplied in a normal pathway
workflow.

## Pathway and data arguments

| Argument | Default | What it controls |
| --- | --- | --- |
| `pathway_id` | required | KEGG pathway number such as `"04110"` or full ID such as `"hsa04110"` |
| `gene_data` | `None` | Polars DataFrame whose first column contains gene or KO IDs |
| `cpd_data` | `None` | Polars DataFrame whose first column contains compound IDs |
| `species` | `"hsa"` | KEGG organism code, or `"ko"` for a KO reference pathway |
| `kegg_dir` | `"."` | folder for downloaded pathway files and finished images |
| `gene_idtype` | `"ENTREZ"` | identifier system used by the first gene-data column |
| `cpd_idtype` | `"KEGG"` | identifier system used by the first compound-data column |

Every column after the first data-table column is treated as a measurement
column. One measurement produces one color per mapped node. Several
measurement columns produce several color sections per mapped node.

## Output and mapping arguments

| Argument | Default | What it controls |
| --- | --- | --- |
| `kegg_native` | `True` | select the KEGG-picture renderer for PNG; use `False` for the structured SVG or PDF routes |
| `output_format` | `"png"` | choose `"png"`, `"svg"`, or `"pdf"` |
| `out_suffix` | `"pathview"` | text added to the finished filename |
| `node_sum` | `"sum"` | combine several input rows that map to one pathway node |
| `map_symbol` | `True` | request gene-symbol labels for mapped Entrez genes |
| `map_null` | `True` | keep a position-only gene or compound layer when that data table is not supplied |
| `min_nnodes` | `3` | minimum number of mappable pathway nodes |
| `new_signature` | `True` | include the Pathview Plus rendering signature |
| `plot_col_key` | `True` | include the color key in native PNG or graph PDF output |
| `na_col` | `"transparent"` | color assigned to a missing value |
| `**kwargs` | none | pass an additional graph-renderer setting, such as `cex=0.8` |

The available `node_sum` choices are:

| Choice | Combination rule |
| --- | --- |
| `"sum"` | add the mapped values |
| `"mean"` | calculate their mean |
| `"median"` | calculate their median |
| `"max"` | keep the largest value |
| `"max_abs"` | keep the value with the largest absolute magnitude |
| `"random"` | choose one mapped value |

## Color arguments

Color arguments use dictionaries so gene and compound data can have separate
settings.

```python
limit = {"gene": 2.0, "cpd": 1.5}
bins = {"gene": 20, "cpd": 10}
both_dirs = {"gene": True, "cpd": True}
discrete = {"gene": False, "cpd": False}
low = {"gene": "#2166AC", "cpd": "#1B7837"}
mid = {"gene": "#F7F7F7", "cpd": "#F7F7F7"}
high = {"gene": "#B2182B", "cpd": "#762A83"}
trans_fun = {"gene": None, "cpd": None}
```

| Argument | Standard gene value | Standard compound value | Meaning |
| --- | ---: | ---: | --- |
| `limit` | `1.0` | `1.0` | color-scale endpoint |
| `bins` | `10` | `10` | number of color levels |
| `both_dirs` | `True` | `True` | use a negative-to-positive scale |
| `discrete` | `False` | `False` | discrete-data setting |
| `low` | `"green"` | `"blue"` | low-end color |
| `mid` | `"gray"` | `"gray"` | midpoint color |
| `high` | `"red"` | `"yellow"` | high-end color |
| `trans_fun` | `None` | `None` | optional numerical transformation |

When a color argument is omitted, Pathview Plus fills in the standard values
shown above.

## Return value

`pathview()` returns a dictionary:

```python
result = pathview(...)

gene_nodes = result["plot_data_gene"]
compound_nodes = result["plot_data_cpd"]
```

| Key | Value |
| --- | --- |
| `"plot_data_gene"` | mapped gene-node table, or `None` when gene data was not used |
| `"plot_data_cpd"` | mapped compound-node table, or `None` when compound data was not used |

These tables contain pathway positions and mapped measurements. The
[highlighting workflow](21-highlighting.md) shows one advanced use for them.

## Data-generation and aggregation functions

Import:

```python
from pathview import mol_sum, sim_mol_data
```

### `sim_mol_data`

```python
sim_mol_data(
    mol_type="gene",
    species="hsa",
    n_mol=100,
    n_exp=1,
    rand_seed=100,
    discrete=False,
)
```

Returns a Polars DataFrame with an `id` column and simulated columns named
`exp1`, `exp2`, and so on.

### `mol_sum`

```python
mol_sum(mol_data, id_map, sum_method="sum")
```

Uses a two-column ID map to move source IDs to target IDs and combine rows that
share a target.

## Identifier functions

Import:

```python
from pathview import cpd_id_map, eg2id, id2eg
```

| Function | Signature | Purpose |
| --- | --- | --- |
| `id2eg` | `id2eg(ids, category, org="Hs")` | map a gene identifier type to Entrez IDs |
| `eg2id` | `eg2id(eg_ids, category="SYMBOL", org="Hs")` | map Entrez IDs to another gene identifier type |
| `cpd_id_map` | `cpd_id_map(in_ids, in_type, out_type="KEGG")` | map compound identifiers between systems |

These functions return two-column Polars DataFrames. See
[Identifier conversion](16-identifier-conversion.md) for complete examples.

## KEGG retrieval and parsing

Import:

```python
from pathview import (
    KGMLEdge,
    KGMLNode,
    KGMLPathway,
    KGMLReaction,
    SpeciesInfo,
    download_kegg,
    kegg_species_code,
    node_info,
    parse_kgml,
)
```

| Name | Signature or role |
| --- | --- |
| `kegg_species_code` | `kegg_species_code(species="hsa")` resolves species metadata |
| `download_kegg` | `download_kegg(pathway_id, species="hsa", kegg_dir=Path("."), file_type=None)` downloads KGML and pathway-image files |
| `parse_kgml` | `parse_kgml(filepath)` converts a KGML XML file into a `KGMLPathway` |
| `node_info` | `node_info(pathway)` converts pathway nodes into a Polars DataFrame |
| `SpeciesInfo` | stores KEGG species metadata |
| `KGMLPathway` | stores pathway ID, name, nodes, edges, and reactions |
| `KGMLNode` | stores one KGML entry |
| `KGMLEdge` | stores one KGML relation |
| `KGMLReaction` | stores one KGML reaction |

## Node mapping and colors

Import:

```python
from pathview import (
    draw_color_key,
    make_colormap,
    node_color,
    node_map,
)
```

| Function | Signature | Purpose |
| --- | --- | --- |
| `node_map` | `node_map(mol_data, node_data, node_types="gene", node_sum="sum", entrez_gnodes=True)` | join measurements to pathway nodes |
| `make_colormap` | `make_colormap(low="green", mid="gray", high="red", n=256)` | make a three-color Matplotlib map |
| `node_color` | `node_color(plot_data, limit=1.0, bins=10, both_dirs=True, discrete=False, low="green", mid="gray", high="red", na_col="transparent", trans_fun=None)` | convert node values into hex colors |
| `draw_color_key` | `draw_color_key(ax, limit=1.0, bins=10, both_dirs=True, discrete=False, low="green", mid="gray", high="red", label_size=8)` | draw a color key on a Matplotlib axis |

## Rendering functions

Most users select a renderer through `pathview()`. The renderers are also
public for advanced workflows.

```python
from pathview import (
    kegg_legend,
    keggview_graph,
    keggview_native,
    keggview_svg,
    render_edge_svg,
    render_node_svg,
)
```

| Function | Result |
| --- | --- |
| `keggview_native(...)` | colored KEGG-background PNG |
| `keggview_graph(...)` | graph-layout PDF |
| `keggview_svg(...)` | standalone pathway SVG |
| `kegg_legend(legend_type="both")` | KEGG node-and-edge reference legend |
| `render_node_svg(...)` | SVG text for one node |
| `render_edge_svg(...)` | SVG text for one edge |

The direct `keggview_*` functions receive mapped node tables, color tables,
node metadata, and output settings. The main `pathview()` function prepares
those inputs automatically.

Their complete call patterns are:

```python
keggview_native(
    plot_data_gene,
    cols_gene,
    plot_data_cpd,
    cols_cpd,
    node_data,
    pathway_name,
    kegg_dir=Path("."),
    out_suffix="pathview",
    limit=None,
    bins=None,
    both_dirs=None,
    discrete=None,
    low=None,
    mid=None,
    high=None,
    new_signature=True,
    plot_col_key=True,
    dpi=150,
)
```

```python
keggview_graph(
    plot_data_gene,
    cols_gene,
    plot_data_cpd,
    cols_cpd,
    node_data,
    pathway_name,
    out_suffix="pathview",
    kegg_dir=Path("."),
    cex=0.7,
    limit=None,
    bins=None,
    both_dirs=None,
    low=None,
    mid=None,
    high=None,
    new_signature=True,
    plot_col_key=True,
)
```

```python
keggview_svg(
    plot_data_gene,
    cols_gene,
    plot_data_cpd,
    cols_cpd,
    node_data,
    pathway_name,
    kegg_dir=Path("."),
    out_suffix="pathview",
    new_signature=True,
    **kwargs,
)
```

```python
kegg_legend(legend_type="both")
```

`legend_type` can be `"both"`, `"edge"`, or `"node"`.

The individual SVG element functions are:

```python
render_node_svg(
    node_id,
    x,
    y,
    width,
    height,
    shape,
    label,
    fill_colors,
    opacity=1.0,
)

render_edge_svg(
    source_x,
    source_y,
    target_x,
    target_y,
    edge_type="arrow",
    color="#666",
    width=1.5,
)
```

`render_node_svg()` accepts rectangle, rounded-rectangle, and ellipse shapes.
`render_edge_svg()` accepts arrow, inhibition, and dotted edge styles. Both
return SVG text.

## SBGN and pathway-database functions

Import:

```python
from pathview import (
    DATABASE_INFO,
    SBGN_ARC_CLASSES,
    SBGN_GLYPH_CLASSES,
    SBGNArc,
    SBGNGlyph,
    SBGNPathway,
    detect_database,
    download_metacyc,
    download_panther,
    download_reactome,
    download_smpdb,
    list_reactome_pathways,
    parse_sbgn,
    sbgn_to_df,
)
```

| Name | Purpose |
| --- | --- |
| `detect_database(pathway_id)` | identify a database from an ID pattern |
| `DATABASE_INFO` | describe database names, URLs, and ID patterns |
| `list_reactome_pathways(species="Homo sapiens")` | return Reactome pathway records |
| `download_reactome(...)` | retrieve a Reactome SBGN-ML file |
| `download_metacyc(...)` | retrieve a MetaCyc SBGN-ML file |
| `download_panther(...)` | PANTHER pathway-file helper |
| `download_smpdb(...)` | SMPDB pathway-file helper |
| `parse_sbgn(filepath)` | parse an SBGN-ML file |
| `sbgn_to_df(pathway)` | convert parsed glyphs into a Polars DataFrame |
| `SBGNPathway` | store glyphs, arcs, and compartments |
| `SBGNGlyph` | store one SBGN glyph |
| `SBGNArc` | store one SBGN arc |
| `SBGN_GLYPH_CLASSES` | describe recognized glyph classes |
| `SBGN_ARC_CLASSES` | describe recognized arc classes |

See [SBGN and pathway databases](20-sbgn-and-databases.md) for the complete
workflow.

The database function signatures are:

```python
download_reactome(
    pathway_id,
    output_dir=Path("."),
    species="Homo sapiens",
)

download_metacyc(pathway_id, output_dir=Path("."))
download_panther(pathway_id, output_dir=Path("."))
download_smpdb(pathway_id, output_dir=Path("."))
list_reactome_pathways(species="Homo sapiens")
detect_database(pathway_id)
```

The four download helpers return a saved `Path` when a file is supplied by the
selected workflow, or `None`. `list_reactome_pathways()` returns a list of
records with `id`, `name`, and `species`. `detect_database()` returns a
lowercase database name or `None`.

The parsed SBGN containers store:

| Class | Public fields |
| --- | --- |
| `SBGNPathway` | `pathway_id`, `pathway_name`, `glyphs`, `arcs`, `compartments` |
| `SBGNGlyph` | `glyph_id`, `glyph_class`, `label`, `x`, `y`, `width`, `height`, `compartment`, `clone_marker`, `state_variables`, `unit_of_information` |
| `SBGNArc` | `arc_id`, `arc_class`, `source`, `target`, `spline_points` |

## Highlighting functions

Import:

```python
from pathview import (
    PathwayResult,
    change_labels,
    highlight_edges,
    highlight_nodes,
    highlight_path,
)
```

| Name | Purpose |
| --- | --- |
| `PathwayResult(...)` | hold an image array and its mapped node tables |
| `highlight_nodes(node_ids, color="red", width=4, opacity=1.0)` | create a node-border modifier |
| `highlight_edges(edge_pairs, color="blue", width=3)` | create an edge modifier |
| `highlight_path(path_node_ids, color="orange", node_width=3, edge_width=2)` | create a combined node-and-edge modifier |
| `change_labels(label_map, font_size=11, color="black")` | attach requested label changes |

`PathwayResult` also provides:

```python
result.save("finished.png")
result.show()
```

Its constructor fields are:

```python
PathwayResult(
    pathway_id,
    plot_data_gene=None,
    plot_data_cpd=None,
    output_path=None,
    image_array=None,
    modifications=[],
)
```

Each new instance receives its own empty modifications list. Adding a modifier
with `+` returns a new `PathwayResult`, which allows several highlighting
operations to be composed.

## Curve and SVG-path functions

Import:

```python
from pathview import (
    bezier_to_svg_path,
    catmull_rom_spline,
    cubic_bezier,
    quadratic_bezier,
    route_edge_spline,
    smooth_path_svg,
)
```

| Function | Purpose |
| --- | --- |
| `cubic_bezier(p0, p1, p2, p3, n_points=50)` | sample a four-point cubic Bézier curve |
| `quadratic_bezier(p0, p1, p2, n_points=50)` | sample a three-point quadratic Bézier curve |
| `catmull_rom_spline(points, n_points=50, alpha=0.5)` | build a curve through control points |
| `route_edge_spline(source, target, obstacles=None, routing_mode="orthogonal")` | generate straight, orthogonal, or curved edge points |
| `bezier_to_svg_path(curve, close=False)` | convert a coordinate array to SVG path data |
| `smooth_path_svg(points, tension=0.5)` | make smooth SVG path commands from waypoints |

## General utilities

Import:

```python
from pathview import max_abs, random_pick, wordwrap
```

| Function | Purpose |
| --- | --- |
| `wordwrap(text, width=20, break_word=False)` | wrap a label into shorter lines |
| `max_abs(values)` | return the value with the largest absolute magnitude |
| `random_pick(values)` | choose one non-missing value |

`max_abs` and `random_pick` are also used by the matching `node_sum` choices.

[<- Previous: Curves and SVG building blocks](22-curves-and-svg.md) | [Home](index.md) | [Next: Citation and support ->](24-citation-and-support.md)
