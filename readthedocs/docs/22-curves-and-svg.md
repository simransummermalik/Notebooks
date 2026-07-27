# Build custom curves and SVG elements

*Page 22 of 24*

Use this page when you want to build a custom vector diagram or create smooth
coordinates for pathway connections.

These are **standalone custom visualization tools**. For a complete KEGG
pathway, the shortest workflow remains:

```python
pathview(
    ...,
    kegg_native=False,
    output_format="svg",
)
```

See [page 15](15-output-formats.md) for the PNG, SVG, and PDF workflow. The
lower-level functions here are useful when you are designing individual SVG
nodes, edges, and paths yourself.

## SVG in one minute

SVG stands for Scalable Vector Graphics. An SVG file is text containing drawing
elements such as:

```xml
<rect ... />
<line ... />
<path ... />
<text ... />
```

Because the drawing is stored as shapes and coordinates, it can be enlarged
without turning into visible pixels.

## 1. Make a small SVG with two nodes and one edge

Save this complete script as `custom_svg.py`:

```python
from pathlib import Path

from pathview import render_edge_svg, render_node_svg


edge = render_edge_svg(
    source_x=130,
    source_y=80,
    target_x=210,
    target_y=80,
    edge_type="arrow",
    color="#4D4D4D",
    width=2,
)

first_node = render_node_svg(
    node_id="gene_a",
    x=80,
    y=80,
    width=100,
    height=40,
    shape="roundedrectangle",
    label="Gene A",
    fill_colors=["#2166AC", "#F7F7F7"],
)

second_node = render_node_svg(
    node_id="gene_b",
    x=260,
    y=80,
    width=100,
    height=40,
    shape="roundedrectangle",
    label="Gene B",
    fill_colors=["#F7F7F7", "#B2182B"],
)

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="340" height="160" viewBox="0 0 340 160">
  <style>
    .node {{ stroke: #333333; stroke-width: 1; }}
    .edge {{ fill: none; }}
    .label {{
      font-family: Arial, sans-serif;
      font-size: 11px;
      text-anchor: middle;
    }}
  </style>
  {edge}
  {first_node}
  {second_node}
</svg>
"""

Path("custom_nodes.svg").write_text(svg, encoding="utf-8")
print("Finished! Open custom_nodes.svg")
```

Run it:

```bash
python custom_svg.py
```

### Understand the node helper

`render_node_svg()` returns an SVG text fragment for you to place inside an
SVG document.

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
```

| Argument | Meaning |
| --- | --- |
| `node_id` | unique text used in the SVG element IDs |
| `x`, `y` | center of the node |
| `width`, `height` | node dimensions |
| `shape` | `"rectangle"`, `"ellipse"`, or `"roundedrectangle"` |
| `label` | text placed at the node center |
| `fill_colors` | one or more fill colors |
| `opacity` | fill opacity from `0.0` to `1.0` |

Several `fill_colors` divide the node into equal vertical sections. This is a
lower-level version of the multi-condition idea introduced on
[page 7](07-multiple-gene-conditions.md).

### Understand the edge helper

`render_edge_svg()` also returns a text fragment:

```python
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

It returns an SVG marker definition and a `<line>` element. The public edge
types are:

| `edge_type` | SVG fragment behavior |
| --- | --- |
| `"arrow"` | solid line with an end marker |
| `"inhibition"` | solid line with an inhibition-named end marker |
| `"dotted"` | dashed line with a dotted-named end marker |

Use a separate biological legend to explain what a custom edge represents.

## 2. Create sampled curves and SVG path data

The curve helpers return NumPy arrays of `(x, y)` coordinates. The SVG helpers
turn coordinates into a string suitable for the `d` attribute of an SVG
`<path>`.

Save this complete example as `custom_curves.py`:

```python
from pathlib import Path

from pathview import (
    bezier_to_svg_path,
    catmull_rom_spline,
    cubic_bezier,
    quadratic_bezier,
    route_edge_spline,
    smooth_path_svg,
)


cubic = cubic_bezier(
    (20, 80),
    (80, 10),
    (180, 10),
    (240, 80),
    n_points=60,
)

quadratic = quadratic_bezier(
    (20, 170),
    (130, 100),
    (240, 170),
    n_points=50,
)

catmull_rom = catmull_rom_spline(
    [(20, 260), (80, 200), (170, 270), (240, 210)],
    n_points=20,
    alpha=0.0,
)

routed = route_edge_spline(
    source=(20, 330),
    target=(240, 390),
    obstacles=[],
    routing_mode="curved",
)

cubic_path = bezier_to_svg_path(cubic)
quadratic_path = bezier_to_svg_path(quadratic)
catmull_path = bezier_to_svg_path(catmull_rom)
routed_path = bezier_to_svg_path(routed)

waypoint_path = smooth_path_svg(
    [(20, 470), (80, 420), (170, 490), (240, 430)]
)

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="270" height="520" viewBox="0 0 270 520">
  <rect width="270" height="520" fill="#FFFFFF"/>
  <path d="{cubic_path}" stroke="#2166AC"
        stroke-width="3" fill="none"/>
  <path d="{quadratic_path}" stroke="#B2182B"
        stroke-width="3" fill="none"/>
  <path d="{catmull_path}" stroke="#1B7837"
        stroke-width="3" fill="none"/>
  <path d="{routed_path}" stroke="#762A83"
        stroke-width="3" fill="none"/>
  <path d="{waypoint_path}" stroke="#E08214"
        stroke-width="3" fill="none"/>
</svg>
"""

Path("custom_curves.svg").write_text(svg, encoding="utf-8")
print("Finished! Open custom_curves.svg")
```

Run it:

```bash
python custom_curves.py
```

## Curve function reference

### Cubic Bezier

```python
cubic_bezier(p0, p1, p2, p3, n_points=50)
```

A cubic Bezier has a start point, two control points, and an end point. It
returns a NumPy array with shape `(n_points, 2)`.

### Quadratic Bezier

```python
quadratic_bezier(p0, p1, p2, n_points=50)
```

A quadratic Bezier has a start point, one control point, and an end point. It
also returns an array with shape `(n_points, 2)`.

### Catmull-Rom spline

```python
catmull_rom_spline(points, n_points=50, alpha=0.5)
```

A Catmull-Rom spline passes through its supplied control points. `n_points` is
the number sampled between each pair. The parameterization choices are:

| `alpha` | Name |
| ---: | --- |
| `0.0` | uniform |
| `0.5` | centripetal |
| `1.0` | chordal |

The complete example uses the uniform setting explicitly.

### Route an edge

```python
route_edge_spline(
    source,
    target,
    obstacles=None,
    routing_mode="orthogonal",
)
```

| Setting | Returned coordinates |
| --- | --- |
| `routing_mode="straight"` | source and target points |
| `routing_mode="orthogonal"` with an obstacle list | a sampled Manhattan-style route |
| `routing_mode="curved"` with an obstacle list | 30 points sampled from a gentle cubic curve |
| `obstacles=None` | source and target points |

For an orthogonal or curved route, pass an `obstacles` list. An empty list
selects the requested routing style when there are no rectangles to provide.
Obstacle rectangles use `(x, y, width, height)` tuples.

### Convert sampled points to SVG

```python
bezier_to_svg_path(curve, close=False)
```

This function starts with an SVG `M` command and adds an `L` command for each
remaining sampled point. `close=True` adds `Z` to close the shape.

```python
smooth_path_svg(points, tension=0.5)
```

This function creates an SVG path string directly from waypoints. It begins
with `M`, uses `Q` for the first curve segment, and uses `T` for later smooth
continuations. `tension` remains part of the public function signature.

## Lower-level KEGG renderer reference

Most users select a renderer with `pathview()`. These public functions expose
the individual rendering stages:

| Function | Main output | Important settings |
| --- | --- | --- |
| `keggview_native(...)` | `<pathway>.<suffix>.png` | overlays colors on a KEGG PNG; `dpi=150` |
| `keggview_graph(...)` | `<pathway>.<suffix>.pdf` | draws a graph at pathway coordinates; `cex=0.7` |
| `keggview_svg(...)` | `<pathway>.<suffix>.svg` | draws mapped nodes as vector elements |
| `kegg_legend(legend_type="both")` | displayed KEGG reference legend | `"both"`, `"edge"`, or `"node"` |

The three renderer functions take mapped gene and compound tables, their color
tables, the complete node table, a pathway name, and output settings. The
[complete API reference](23-api-reference.md) lists their signatures and public
imports.

## Choose the right level

| Your goal | Recommended tool |
| --- | --- |
| create a complete KEGG image | `pathview()` |
| create an SVG node fragment | `render_node_svg()` |
| create an SVG line fragment | `render_edge_svg()` |
| calculate smooth coordinates | a Bezier or spline function |
| turn sampled coordinates into SVG path data | `bezier_to_svg_path()` |
| work directly with a renderer | a `keggview_*` function |

[<- Previous: Highlight a finished pathway](21-highlighting.md) | [Home](index.md) | [Next: Complete API reference ->](23-api-reference.md)
