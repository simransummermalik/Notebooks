from __future__ import annotations

import hashlib
from pathlib import Path
from xml.etree import ElementTree as ET

import networkx as nx
import numpy as np
import polars as pl
import pytest
from PIL import Image

from pathview import keggview_graph, keggview_native, keggview_svg, render_edge_svg, render_node_svg
from pathview.rendering import _hex_to_rgb255, _paint_cpd_nodes, _paint_gene_nodes


def _one_gene(y: float = 20.0) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "entry_id": ["1"],
            "name": ["hsa:1029"],
            "type": ["gene"],
            "x": [30.0],
            "y": [y],
            "width": [40.0],
            "height": [20.0],
            "label": ["CDKN2A"],
            "shape": ["rectangle"],
            "kegg_names": ["1029"],
        }
    )


def _one_compound(y: float = 20.0, width: float = 10.0, height: float = 10.0) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "entry_id": ["3"],
            "name": ["cpd:C00031"],
            "type": ["compound"],
            "x": [55.0],
            "y": [y],
            "width": [width],
            "height": [height],
            "label": ["Glucose"],
            "shape": ["circle"],
            "kegg_names": ["C00031"],
        }
    )


@pytest.mark.rendering
@pytest.mark.parametrize(
    ("colors", "sample_x", "expected"),
    [
        (["#00FF00"], [15, 45], [[0, 255, 0], [0, 255, 0]]),
        (["#00FF00", "#FF0000"], [15, 45], [[0, 255, 0], [255, 0, 0]]),
        (
            ["#0000FF", "#BEBEBE", "#FF0000"],
            [15, 30, 45],
            [[0, 0, 255], [190, 190, 190], [255, 0, 0]],
        ),
    ],
)
def test_gene_node_one_two_three_state_slices(colors, sample_x, expected) -> None:
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    color_frame = {"id": ["1"]}
    for index, color in enumerate(colors):
        color_frame[f"state_{index}_col"] = [color]
    painted = _paint_gene_nodes(image, _one_gene(), pl.DataFrame(color_frame))
    for x, rgb in zip(sample_x, expected):
        assert np.array_equal(painted[20, x], np.array(rgb, dtype=np.uint8))


@pytest.mark.rendering
def test_gene_paint_preserves_existing_black_text_and_border_pixels() -> None:
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    image[20, 30] = 0
    colors = pl.DataFrame({"id": ["1"], "state_col": ["#00FF00"]})
    painted = _paint_gene_nodes(image, _one_gene(), colors)
    assert np.array_equal(painted[20, 30], [0, 0, 0])
    assert np.array_equal(painted[20, 20], [0, 255, 0])


@pytest.mark.rendering
def test_transparent_gene_slice_leaves_background_unchanged() -> None:
    image = np.full((100, 100, 3), 231, dtype=np.uint8)
    colors = pl.DataFrame(
        {"id": ["1"], "left_col": ["transparent"], "right_col": ["#FF0000"]}
    )
    painted = _paint_gene_nodes(image, _one_gene(), colors)
    assert np.array_equal(painted[20, 15], [231, 231, 231])
    assert np.array_equal(painted[20, 45], [255, 0, 0])


@pytest.mark.rendering
def test_compound_two_state_left_right_split_at_center() -> None:
    image = np.full((100, 110, 3), 255, dtype=np.uint8)
    colors = pl.DataFrame(
        {"id": ["3"], "left_col": ["#0000FF"], "right_col": ["#FF0000"]}
    )
    painted = _paint_cpd_nodes(image, _one_compound(y=50), colors)
    assert np.array_equal(painted[50, 51], [0, 0, 255])
    assert np.array_equal(painted[50, 59], [255, 0, 0])


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-029: compound y coordinates are flipped while gene y coordinates are effectively not"
)
def test_gene_and_compound_use_same_coordinate_system() -> None:
    gene_image = np.full((100, 110, 3), 255, dtype=np.uint8)
    cpd_image = gene_image.copy()
    gene = _paint_gene_nodes(
        gene_image,
        _one_gene(y=20),
        pl.DataFrame({"id": ["1"], "value_col": ["#00FF00"]}),
    )
    cpd = _paint_cpd_nodes(
        cpd_image,
        _one_compound(y=20),
        pl.DataFrame({"id": ["3"], "value_col": ["#FF0000"]}),
    )
    assert np.array_equal(gene[20, 30], [0, 255, 0])
    assert np.array_equal(cpd[20, 55], [255, 0, 0])


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-030: compound KGML width is treated as radius instead of diameter"
)
def test_compound_width_is_the_full_display_diameter() -> None:
    image = np.full((100, 110, 3), 255, dtype=np.uint8)
    painted = _paint_cpd_nodes(
        image,
        _one_compound(y=50, width=10, height=10),
        pl.DataFrame({"id": ["3"], "value_col": ["#FF0000"]}),
    )
    assert np.array_equal(painted[50, 63], [255, 255, 255])


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-031: compound height is ignored and all compounds are forced to width-based circles"
)
def test_compound_renderer_respects_elliptical_height() -> None:
    image = np.full((100, 110, 3), 255, dtype=np.uint8)
    painted = _paint_cpd_nodes(
        image,
        _one_compound(y=50, width=20, height=8),
        pl.DataFrame({"id": ["3"], "value_col": ["#FF0000"]}),
    )
    assert np.array_equal(painted[60, 55], [255, 255, 255])


@pytest.mark.rendering
@pytest.mark.parametrize(
    ("value", "expected"),
    [("#FF0000", [255, 0, 0]), ("transparent", None), ("none", None)],
)
def test_native_hex_color_conversion(value, expected) -> None:
    result = _hex_to_rgb255(value)
    if expected is None:
        assert result is None
    else:
        assert np.array_equal(result, expected)


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-032: native/highlight renderers advertise named colors but parse only six-digit hex"
)
def test_native_color_converter_accepts_named_matplotlib_colors() -> None:
    assert np.array_equal(_hex_to_rgb255("red"), [255, 0, 0])


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-033: three-digit CSS hex colors are not accepted"
)
def test_native_color_converter_accepts_short_hex() -> None:
    assert np.array_equal(_hex_to_rgb255("#F00"), [255, 0, 0])


@pytest.mark.rendering
def test_native_renderer_requires_background_png(tmp_path: Path, simple_node_data) -> None:
    with pytest.raises(FileNotFoundError, match="Background PNG"):
        keggview_native(
            None,
            None,
            None,
            None,
            simple_node_data,
            "hsa00001",
            kegg_dir=tmp_path,
            plot_col_key=False,
        )


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-034: bbox_inches='tight' crops/rescales native output instead of preserving KEGG pixels"
)
def test_native_output_preserves_background_dimensions(tmp_path: Path, simple_node_data) -> None:
    source = tmp_path / "hsa00001.png"
    Image.new("RGB", (120, 100), "white").save(source)
    keggview_native(
        None,
        None,
        None,
        None,
        simple_node_data,
        "hsa00001",
        kegg_dir=tmp_path,
        out_suffix="dimensions",
        new_signature=False,
        plot_col_key=False,
        dpi=100,
    )
    with Image.open(tmp_path / "hsa00001.dimensions.png") as output:
        assert output.size == (120, 100)


@pytest.mark.rendering
def test_native_render_is_repeatable_for_identical_inputs(tmp_path: Path, simple_node_data) -> None:
    Image.new("RGB", (120, 100), "white").save(tmp_path / "hsa00001.png")
    kwargs = dict(
        plot_data_gene=_one_gene(),
        cols_gene=pl.DataFrame({"id": ["1"], "value_col": ["#00FF00"]}),
        plot_data_cpd=None,
        cols_cpd=None,
        node_data=simple_node_data,
        pathway_name="hsa00001",
        kegg_dir=tmp_path,
        out_suffix="repeat",
        new_signature=False,
        plot_col_key=False,
    )
    keggview_native(**kwargs)
    first = hashlib.sha256((tmp_path / "hsa00001.repeat.png").read_bytes()).hexdigest()
    keggview_native(**kwargs)
    second = hashlib.sha256((tmp_path / "hsa00001.repeat.png").read_bytes()).hexdigest()
    assert first == second


@pytest.mark.rendering
@pytest.mark.parametrize("states", [1, 2, 3])
def test_svg_rectangle_has_equal_ordered_state_slices(states: int) -> None:
    colors = ["#0000FF", "#BEBEBE", "#FF0000"][:states]
    snippet = render_node_svg("node1", 50, 30, 42, 18, "rectangle", "TP53", colors)
    root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{snippet}</svg>')
    rects = [element for element in root.iter() if element.tag.endswith("rect")]
    assert len(rects) == states
    assert [float(r.attrib["width"]) for r in rects] == pytest.approx([42 / states] * states)
    assert [r.attrib["fill"] for r in rects] == colors


@pytest.mark.rendering
def test_svg_ellipse_uses_clip_slices_and_valid_xml() -> None:
    snippet = render_node_svg(
        "cpd1", 50, 30, 20, 10, "ellipse", "ATP", ["#0000FF", "#FF0000"]
    )
    root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{snippet}</svg>')
    ellipses = [element for element in root.iter() if element.tag.endswith("ellipse")]
    clips = [element for element in root.iter() if element.tag.endswith("clipPath")]
    assert len(ellipses) == 2
    assert len(clips) == 2


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-068: KGML shape='circle' is sent to SVG but only shape='ellipse' renders an ellipse"
)
def test_svg_renders_kgml_circle_as_circle() -> None:
    snippet = render_node_svg(
        "cpd1", 50, 30, 20, 20, "circle", "ATP", ["#0000FF", "#FF0000"]
    )
    root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{snippet}</svg>')
    assert any(element.tag.endswith("ellipse") for element in root.iter())
    assert not any(element.tag.endswith("rect") and "fill" in element.attrib for element in root.iter())


@pytest.mark.rendering
def test_svg_labels_escape_xml_characters() -> None:
    snippet = render_node_svg(
        "node1", 50, 30, 60, 20, "rectangle", 'A&B <C> "D"', ["#FFFFFF"]
    )
    root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{snippet}</svg>')
    text = "".join(root.itertext())
    assert "A&B <C>" in text
    assert '"D"' in text


@pytest.mark.rendering
def test_svg_edge_snippet_is_valid_and_has_marker() -> None:
    snippet = render_edge_svg(0, 0, 50, 50, edge_type="arrow")
    ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{snippet}</svg>')
    assert "marker-end" in snippet


@pytest.mark.rendering
def test_complete_svg_output_is_valid_xml(
    tmp_path: Path, simple_node_data, simple_gene_plot, simple_compound_plot
) -> None:
    genes = pl.DataFrame(
        {"id": ["1", "2"], "A_col": ["#00FF00", "#FF0000"], "B_col": ["#FF0000", "#00FF00"]}
    )
    cpds = pl.DataFrame({"id": ["3"], "A_col": ["#0000FF"], "B_col": ["#FFFF00"]})
    keggview_svg(
        simple_gene_plot,
        genes,
        simple_compound_plot,
        cpds,
        simple_node_data,
        "hsa00001",
        kegg_dir=tmp_path,
        out_suffix="valid",
        new_signature=False,
    )
    output = tmp_path / "hsa00001.valid.svg"
    root = ET.parse(output).getroot()
    assert root.tag.endswith("svg")
    assert output.stat().st_size > 500


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-069: all-transparent SVG nodes are forcibly recolored gray"
)
def test_svg_preserves_transparent_unmapped_nodes(
    tmp_path: Path, simple_node_data, simple_gene_plot
) -> None:
    colors = pl.DataFrame(
        {"id": ["1", "2"], "A_col": ["transparent", "transparent"]}
    )
    keggview_svg(
        simple_gene_plot,
        colors,
        None,
        None,
        simple_node_data,
        "hsa00001",
        kegg_dir=tmp_path,
        out_suffix="transparent",
        new_signature=False,
    )
    text = (tmp_path / "hsa00001.transparent.svg").read_text(encoding="utf-8")
    assert "#CCCCCC" not in text
    assert 'fill="transparent"' in text


@pytest.mark.rendering
@pytest.mark.xfail(reason="PV-BUG-035: SVG document title is not XML-escaped")
def test_svg_pathway_title_with_special_characters_is_valid(
    tmp_path: Path, simple_node_data
) -> None:
    keggview_svg(
        None,
        None,
        None,
        None,
        simple_node_data,
        "A&B <pathway>",
        kegg_dir=tmp_path,
        out_suffix="special",
        new_signature=False,
    )
    ET.parse(tmp_path / "A&B <pathway>.special.svg")


@pytest.mark.rendering
@pytest.mark.xfail(reason="PV-BUG-036: SVG clip IDs interpolate unescaped node identifiers")
def test_svg_ellipse_accepts_special_node_identifiers() -> None:
    snippet = render_node_svg(
        "node&1", 50, 30, 20, 10, "ellipse", "ATP", ["#0000FF", "#FF0000"]
    )
    ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{snippet}</svg>')


@pytest.mark.rendering
@pytest.mark.xfail(reason="PV-BUG-037: empty SVG fill list renders text but no node shape")
def test_svg_node_with_no_fill_values_still_has_a_visible_shape() -> None:
    snippet = render_node_svg("n", 10, 10, 20, 10, "rectangle", "node", [])
    root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{snippet}</svg>')
    assert any(element.tag.endswith(("rect", "ellipse")) for element in root.iter())


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-FEATURE-003: main SVG renderer receives no relation data and emits no pathway edges"
)
def test_main_svg_renderer_includes_pathway_edges(
    tmp_path: Path, simple_node_data, simple_gene_plot
) -> None:
    colors = pl.DataFrame({"id": ["1", "2"], "A_col": ["#00FF00", "#FF0000"]})
    keggview_svg(
        simple_gene_plot,
        colors,
        None,
        None,
        simple_node_data,
        "hsa00001",
        kegg_dir=tmp_path,
        out_suffix="edges",
        new_signature=False,
    )
    root = ET.parse(tmp_path / "hsa00001.edges.svg").getroot()
    assert any(element.tag.endswith(("line", "path")) and element.attrib.get("class") == "edge" for element in root.iter())


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-FEATURE-004: graph renderer builds nodes only; KGML relations are not passed into it"
)
def test_graph_renderer_contains_relations(
    tmp_path: Path,
    simple_node_data,
    simple_gene_plot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict = {}

    def capture(graph, *args, **kwargs):
        captured["edges"] = graph.number_of_edges()

    monkeypatch.setattr(nx, "draw_networkx", capture)
    colors = pl.DataFrame({"id": ["1", "2"], "A_col": ["#00FF00", "#FF0000"]})
    keggview_graph(
        simple_gene_plot,
        colors,
        None,
        None,
        simple_node_data,
        "hsa00001",
        kegg_dir=tmp_path,
        out_suffix="edges",
        new_signature=False,
        plot_col_key=False,
    )
    assert captured["edges"] > 0


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-038: graph/PDF renderer uses only the first experiment color"
)
def test_graph_renderer_preserves_two_state_node_colors(
    tmp_path: Path,
    simple_node_data,
    simple_gene_plot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict = {}

    def capture(graph, *args, **kwargs):
        captured["node_colors"] = kwargs["node_color"]

    monkeypatch.setattr(nx, "draw_networkx", capture)
    colors = pl.DataFrame(
        {"id": ["1", "2"], "A_col": ["#00FF00", "#FF0000"], "B_col": ["#FF0000", "#00FF00"]}
    )
    keggview_graph(
        simple_gene_plot,
        colors,
        None,
        None,
        simple_node_data,
        "hsa00001",
        kegg_dir=tmp_path,
        out_suffix="states",
        new_signature=False,
        plot_col_key=False,
    )
    assert isinstance(captured["node_colors"][0], (list, tuple))
    assert len(captured["node_colors"][0]) == 2


@pytest.mark.rendering
def test_graph_renderer_writes_valid_pdf(
    tmp_path: Path, simple_node_data, simple_gene_plot
) -> None:
    colors = pl.DataFrame({"id": ["1", "2"], "A_col": ["#00FF00", "#FF0000"]})
    keggview_graph(
        simple_gene_plot,
        colors,
        None,
        None,
        simple_node_data,
        "hsa00001",
        kegg_dir=tmp_path,
        out_suffix="valid",
        new_signature=False,
        plot_col_key=False,
    )
    output = tmp_path / "hsa00001.valid.pdf"
    assert output.read_bytes().startswith(b"%PDF")
    assert output.stat().st_size > 1_000


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-070: compound-only native color-key layout leaves a blank visible ticked subplot"
)
def test_compound_only_color_key_has_no_blank_subplot(
    tmp_path: Path,
    simple_node_data,
    simple_compound_plot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import matplotlib.pyplot as plt

    original_subplots = plt.subplots
    captured: dict = {}

    def capture_subplots(*args, **kwargs):
        fig, axes = original_subplots(*args, **kwargs)
        captured["axes"] = axes
        return fig, axes

    monkeypatch.setattr(plt, "subplots", capture_subplots)
    Image.new("RGB", (120, 100), "white").save(tmp_path / "hsa00001.png")
    colors = pl.DataFrame({"id": ["3"], "A_col": ["#0000FF"]})
    keggview_native(
        None,
        None,
        simple_compound_plot,
        colors,
        simple_node_data,
        "hsa00001",
        kegg_dir=tmp_path,
        out_suffix="compound_key",
        new_signature=False,
        plot_col_key=True,
    )
    extra_axis = captured["axes"][1]
    assert not extra_axis.get_visible() or extra_axis.has_data()


@pytest.mark.rendering
@pytest.mark.xfail(
    reason="PV-BUG-071: graph color key always uses gene limits/colors, even for compound-only plots"
)
def test_compound_only_graph_uses_compound_color_scale(
    tmp_path: Path,
    simple_node_data,
    simple_compound_plot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import pathview.rendering as rendering_module

    captured: dict = {}

    def capture_key(ax, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(rendering_module, "draw_color_key", capture_key)
    colors = pl.DataFrame({"id": ["3"], "A_col": ["#0000FF"]})
    keggview_graph(
        None,
        None,
        simple_compound_plot,
        colors,
        simple_node_data,
        "hsa00001",
        kegg_dir=tmp_path,
        out_suffix="compound_scale",
        new_signature=False,
        plot_col_key=True,
        limit={"gene": 1, "cpd": 7},
        low={"gene": "green", "cpd": "navy"},
        mid={"gene": "gray", "cpd": "white"},
        high={"gene": "red", "cpd": "yellow"},
    )
    assert captured["limit"] == 7
    assert captured["low"] == "navy"
