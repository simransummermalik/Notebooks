from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import polars as pl
import pytest
from PIL import Image
from importlib.metadata import version

import pathview
from pathview import (
    PathwayResult,
    bezier_to_svg_path,
    catmull_rom_spline,
    cubic_bezier,
    highlight_edges,
    highlight_nodes,
    make_colormap,
    mol_sum,
    node_color,
    node_info,
    parse_kgml,
    parse_sbgn,
    quadratic_bezier,
    render_edge_svg,
    render_node_svg,
    route_edge_spline,
    sbgn_to_df,
    sim_mol_data,
)
from pathview.rendering import _paint_cpd_nodes, _paint_gene_nodes


ROOT = Path(__file__).resolve().parents[1]


def _node_frame(entry_id: str = "1", name: str = "hsa:1029") -> pl.DataFrame:
    return pl.DataFrame({
        "entry_id": [entry_id],
        "name": [name],
        "type": ["gene"],
        "x": [50.0],
        "y": [50.0],
        "width": [40.0],
        "height": [20.0],
        "bgcolor": ["#FFFFFF"],
        "label": ["CDKN2A"],
        "shape": ["rectangle"],
        "reaction": [""],
        "component": [""],
        "size": [1],
        "kegg_names": ["1029"],
        "Classical": [-1.0],
        "Basal": [1.0],
    })


def test_import_and_packaging_version_are_recorded() -> None:
    assert callable(pathview.pathview)
    assert pathview.__version__ == "2.0.0"


@pytest.mark.xfail(reason="Distribution is 2.0.2 but pathview.__version__ remains 2.0.0")
def test_distribution_and_runtime_versions_match() -> None:
    assert version("pathview-plus") == pathview.__version__


def test_color_mapping_continuous_clipping_nan_and_transform() -> None:
    values = pl.DataFrame({"id": ["a", "b", "c", "d"], "v": [-2.0, 0.0, 2.0, np.nan]})
    colors = node_color(
        values,
        limit=1,
        low="#00FF00",
        mid="#BEBEBE",
        high="#FF0000",
        na_col="transparent",
    )
    assert colors["v_col"][0] == "#00FF00"
    assert colors["v_col"][2] == "#FF0000"
    assert colors["v_col"][3] == "transparent"
    odd_bins = node_color(
        values,
        limit=1,
        bins=11,
        low="#00FF00",
        mid="#BEBEBE",
        high="#FF0000",
        na_col="transparent",
    )
    assert odd_bins["v_col"][1] == "#BEBEBE"
    transformed = node_color(
        values.head(3), limit=2, trans_fun=np.abs, low="#00FF00", mid="#BEBEBE", high="#FF0000"
    )
    assert transformed["v_col"][0] == transformed["v_col"][2]
    assert make_colormap("blue", "white", "red").N == 256


def test_single_state_paints_whole_gene_node() -> None:
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    plot_data = _node_frame().drop("Basal")
    colors = pl.DataFrame({"id": ["1"], "Classical_col": ["#00FF00"]})
    painted = _paint_gene_nodes(image, plot_data, colors)
    expected = np.array([0, 255, 0], dtype=np.uint8)
    assert np.all(painted[50, 35] == expected)
    assert np.all(painted[50, 65] == expected)


def test_two_state_gene_node_is_exact_left_right_half() -> None:
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    colors = pl.DataFrame({
        "id": ["1"],
        "Classical_col": ["#00FF00"],
        "Basal_col": ["#FF0000"],
    })
    painted = _paint_gene_nodes(image, _node_frame(), colors)
    assert np.all(painted[50, 35] == np.array([0, 255, 0]))
    assert np.all(painted[50, 65] == np.array([255, 0, 0]))
    left = painted[40:60, 30:50]
    right = painted[40:60, 50:70]
    assert np.mean(np.all(left == [0, 255, 0], axis=2)) == 1.0
    assert np.mean(np.all(right == [255, 0, 0], axis=2)) == 1.0


def test_three_state_gene_node_uses_ordered_equal_slices() -> None:
    image = np.full((90, 120, 3), 255, dtype=np.uint8)
    plot_data = _node_frame().with_columns(pl.lit(0.0).alias("Middle"))
    colors = pl.DataFrame({
        "id": ["1"],
        "Control_col": ["#0000FF"],
        "Treatment_A_col": ["#BEBEBE"],
        "Treatment_B_col": ["#FF0000"],
    })
    painted = _paint_gene_nodes(image, plot_data, colors)
    assert np.all(painted[50, 35] == [0, 0, 255])
    assert np.all(painted[50, 50] == [190, 190, 190])
    assert np.all(painted[50, 65] == [255, 0, 0])


def test_compound_multi_state_slices() -> None:
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    cpd = _node_frame(name="cpd:C00031").with_columns(
        pl.lit("compound").alias("type"),
        pl.lit(10.0).alias("width"),
        pl.lit(10.0).alias("height"),
    )
    colors = pl.DataFrame({"id": ["1"], "A_col": ["#0000FF"], "B_col": ["#FF0000"]})
    painted = _paint_cpd_nodes(image, cpd, colors)
    assert np.all(painted[50, 47] == [0, 0, 255])
    assert np.all(painted[50, 53] == [255, 0, 0])


def test_svg_two_state_geometry_and_xml_validity() -> None:
    svg = render_node_svg(
        "node1", 50, 30, 40, 20, "rectangle", "CDKN2A", ["#00FF00", "#FF0000"]
    )
    wrapper = f'<svg xmlns="http://www.w3.org/2000/svg">{svg}</svg>'
    root = ET.fromstring(wrapper)
    rects = [element for element in root.iter() if element.tag.endswith("rect")]
    assert len(rects) == 2
    assert [float(r.attrib["width"]) for r in rects] == [20.0, 20.0]
    assert [float(r.attrib["x"]) for r in rects] == [30.0, 50.0]
    assert "marker-end" in render_edge_svg(0, 0, 10, 10)


@pytest.mark.parametrize("method,expected", [
    ("sum", 2.0),
    ("mean", 1.0),
    ("median", 1.0),
    ("max", 3.0),
])
def test_molecule_aggregation_methods(method: str, expected: float) -> None:
    data = pl.DataFrame({"probe": ["a", "b"], "value": [-1.0, 3.0]})
    mapping = pl.DataFrame({"probe": ["a", "b"], "entrez": ["1", "1"]})
    got = mol_sum(data, mapping, sum_method=method)
    assert got.height == 1
    assert got["value"][0] == expected


@pytest.mark.xfail(reason="max_abs aggregation applies a group UDF to scalar elements with current Polars")
def test_max_abs_aggregation() -> None:
    data = pl.DataFrame({"probe": ["a", "b"], "value": [-1.0, 3.0]})
    mapping = pl.DataFrame({"probe": ["a", "b"], "entrez": ["1", "1"]})
    got = mol_sum(data, mapping, sum_method="max_abs")
    assert got["value"][0] == 3.0


def test_simulated_compound_data_is_reproducible() -> None:
    one = sim_mol_data("cpd", n_mol=10, n_exp=3, rand_seed=7)
    two = sim_mol_data("cpd", n_mol=10, n_exp=3, rand_seed=7)
    assert one.equals(two)
    assert one.shape == (10, 4)


def test_kgml_parser_node_relation_and_reaction(tmp_path: Path) -> None:
    kgml = tmp_path / "toy.xml"
    kgml.write_text('''<?xml version="1.0"?>
<pathway name="path:hsa00010" number="00010">
  <entry id="1" name="hsa:1029" type="gene" reaction="rn:R1">
    <graphics name="CDKN2A" x="50" y="40" width="46" height="17" type="rectangle"/>
  </entry>
  <entry id="2" name="cpd:C00031" type="compound">
    <graphics name="Glucose" x="100" y="40" width="8" height="8" type="circle"/>
  </entry>
  <relation entry1="1" entry2="2" type="PPrel"><subtype name="activation" value="--&gt;"/></relation>
  <reaction name="rn:R1" type="irreversible"><substrate id="2"/><product id="1"/></reaction>
</pathway>''')
    parsed = parse_kgml(kgml)
    frame = node_info(parsed)
    assert len(parsed.nodes) == 2 and len(parsed.edges) == 1 and len(parsed.reactions) == 1
    assert frame.shape == (2, 13)
    assert frame.filter(pl.col("type") == "gene")["label"][0] == "CDKN2A"


@pytest.mark.xfail(reason="The current SBGN parser does not namespace-qualify glyph and arc searches")
def test_sbgn_parser_and_unified_dataframe(tmp_path: Path) -> None:
    sbgn = tmp_path / "toy.sbgn"
    sbgn.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<sbgn xmlns="http://sbgn.org/libsbgn/0.2">
  <map id="toy" language="process description">
    <glyph id="g1" class="macromolecule"><label text="TP53"/><bbox x="10" y="20" w="40" h="20"/></glyph>
    <glyph id="g2" class="simple chemical"><label text="ATP"/><bbox x="80" y="20" w="20" h="20"/></glyph>
    <arc id="a1" class="production" source="g1" target="g2"><start x="50" y="30"/><end x="80" y="30"/></arc>
  </map>
</sbgn>''')
    parsed = parse_sbgn(sbgn)
    frame = sbgn_to_df(parsed)
    assert len(parsed.glyphs) == 2 and len(parsed.arcs) == 1
    assert set(frame["type"]) == {"gene", "compound"}
    assert frame.filter(pl.col("entry_id") == "g1")["label"][0] == "TP53"


def test_bezier_and_routing_helpers() -> None:
    cubic = cubic_bezier((0, 0), (1, 2), (3, 2), (4, 0), n_points=10)
    quad = quadratic_bezier((0, 0), (2, 2), (4, 0), n_points=10)
    curved = route_edge_spline((0, 0), (4, 4), routing_mode="curved", obstacles=[])
    np.testing.assert_allclose(cubic[[0, -1]], [[0, 0], [4, 0]])
    np.testing.assert_allclose(quad[[0, -1]], [[0, 0], [4, 0]])
    assert curved.shape == (30, 2)
    assert bezier_to_svg_path(cubic).startswith("M 0.00 0.00")


@pytest.mark.xfail(reason="Current Catmull-Rom endpoint duplication divides by zero and returns NaN")
def test_catmull_rom_documented_default_is_finite() -> None:
    curve = catmull_rom_spline([(0, 0), (1, 2), (3, 1), (4, 3)], n_points=10)
    assert curve.shape[1] == 2
    assert np.isfinite(curve).all()


def test_highlighting_layers_compose_and_save(tmp_path: Path) -> None:
    frame = _node_frame()
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    result = PathwayResult("hsa04110", plot_data_gene=frame, image_array=image)
    modified = result + highlight_nodes(["1029"], color="#FF0000", width=2)
    modified = modified + highlight_edges([("1029", "1029")], color="#0000FF", width=1)
    output = tmp_path / "highlighted.png"
    modified.save(output)
    assert output.exists()
    assert not np.array_equal(modified.image_array, image)
    assert np.array(Image.open(output)).shape[:2] == (100, 100)
