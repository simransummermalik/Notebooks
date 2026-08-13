from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

import polars as pl
import pytest

from pathview import KGMLPathway, node_info, parse_kgml, parse_sbgn, sbgn_to_df


VALID_KGML = """<?xml version="1.0"?>
<pathway name="path:hsa00010" number="00010" title="Glycolysis">
  <entry id="1" name="hsa:1029" type="gene" reaction="rn:R1" link="https://example.test/1">
    <graphics name="CDKN2A" x="50" y="40" width="46" height="17" type="rectangle" bgcolor="#FFFFFF"/>
  </entry>
  <entry id="2" name="cpd:C00031" type="compound">
    <graphics name="Glucose" x="100" y="40" width="8" height="8" type="circle"/>
  </entry>
  <entry id="3" name="undefined" type="group">
    <component id="1"/><component id="2"/>
    <graphics name="group" x="75" y="40" width="70" height="25" type="rectangle"/>
  </entry>
  <relation entry1="1" entry2="2" type="PPrel">
    <subtype name="activation" value="--&gt;"/>
    <subtype name="phosphorylation" value="+p"/>
  </relation>
  <reaction name="rn:R1" type="irreversible">
    <substrate id="2"/><product id="1"/>
  </reaction>
</pathway>
"""


VALID_SBGN_NO_NAMESPACE = """<?xml version="1.0" encoding="UTF-8"?>
<sbgn>
  <map id="toy" language="process description">
    <glyph id="g1" class="macromolecule" compartmentRef="c1">
      <label text="TP53"/><bbox x="10" y="20" w="40" h="20"/>
    </glyph>
    <glyph id="g2" class="simple chemical">
      <label text="ATP"/><bbox x="80" y="20" w="20" h="20"/>
    </glyph>
    <glyph id="c1" class="compartment">
      <label text="cytosol"/><bbox x="0" y="0" w="150" h="100"/>
    </glyph>
    <arc id="a1" class="production" source="g1" target="g2">
      <start x="50" y="30"/><next x="65" y="25"/><end x="80" y="30"/>
    </arc>
  </map>
</sbgn>
"""


VALID_SBGN_NAMESPACED = VALID_SBGN_NO_NAMESPACE.replace(
    "<sbgn>", '<sbgn xmlns="http://sbgn.org/libsbgn/0.2">'
)


@pytest.mark.parser
def test_kgml_nodes_edges_reactions_and_groups(tmp_path: Path) -> None:
    source = tmp_path / "pathway.xml"
    source.write_text(VALID_KGML, encoding="utf-8")
    pathway = parse_kgml(source)
    frame = node_info(pathway)
    assert pathway.pathway_id == "00010"
    assert pathway.pathway_name == "path:hsa00010"
    assert len(pathway.nodes) == 3
    assert len(pathway.edges) == 1
    assert len(pathway.reactions) == 1
    assert pathway.edges[0].subtypes == [
        ("activation", "-->"),
        ("phosphorylation", "+p"),
    ]
    assert pathway.reactions[0].substrates == ["2"]
    group = frame.filter(pl.col("entry_id") == "3")
    assert group["component"][0] == "1;2"
    assert group["size"][0] == 2


@pytest.mark.parser
def test_kgml_entry_without_graphics_retains_null_geometry(tmp_path: Path) -> None:
    source = tmp_path / "missing-graphics.xml"
    source.write_text(
        '<pathway number="1"><entry id="1" name="hsa:1" type="gene"/></pathway>',
        encoding="utf-8",
    )
    frame = node_info(parse_kgml(source))
    assert frame.height == 1
    assert frame["x"][0] is None
    assert frame["width"][0] is None
    assert frame["label"][0] == "hsa:1"


@pytest.mark.parser
def test_malformed_xml_raises_xml_parse_error(tmp_path: Path) -> None:
    source = tmp_path / "broken.xml"
    source.write_text("<pathway><entry></pathway>", encoding="utf-8")
    with pytest.raises(ET.ParseError):
        parse_kgml(source)


@pytest.mark.parser
def test_missing_kgml_file_has_normal_file_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        parse_kgml(tmp_path / "does-not-exist.xml")


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-BUG-019: namespace-qualified KGML child tags are not dispatched"
)
def test_namespace_qualified_kgml_is_parsed(tmp_path: Path) -> None:
    source = tmp_path / "namespaced.xml"
    source.write_text(
        VALID_KGML.replace(
            "<pathway ", '<pathway xmlns="http://www.kegg.jp/kegg/xml/KGML/0.7.2" ', 1
        ),
        encoding="utf-8",
    )
    pathway = parse_kgml(source)
    assert len(pathway.nodes) == 3
    assert len(pathway.edges) == 1


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-BUG-020: duplicate KGML entry IDs silently overwrite earlier entries"
)
def test_duplicate_kgml_entry_ids_are_rejected(tmp_path: Path) -> None:
    source = tmp_path / "duplicates.xml"
    source.write_text(
        """<pathway number="1">
        <entry id="1" name="hsa:1" type="gene"/>
        <entry id="1" name="hsa:2" type="gene"/>
        </pathway>""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate|Duplicate"):
        parse_kgml(source)


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-BUG-021: line graphics coords are ignored and replaced with zero/default geometry"
)
def test_kgml_line_graphics_coordinates_are_preserved(tmp_path: Path) -> None:
    source = tmp_path / "line.xml"
    source.write_text(
        """<pathway number="1"><entry id="1" name="hsa:1" type="gene">
        <graphics name="line" type="line" coords="10,20,30,40"/>
        </entry></pathway>""",
        encoding="utf-8",
    )
    node = parse_kgml(source).nodes["1"]
    assert (node.x, node.y) == (20.0, 30.0)
    assert (node.width, node.height) == (20.0, 20.0)


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-BUG-022: node_info(empty pathway) has no stable columns/schema"
)
def test_empty_kgml_node_table_has_standard_schema() -> None:
    frame = node_info(KGMLPathway(pathway_id="1", pathway_name="empty"))
    assert frame.columns == [
        "entry_id",
        "name",
        "type",
        "x",
        "y",
        "width",
        "height",
        "bgcolor",
        "label",
        "shape",
        "reaction",
        "component",
        "size",
    ]
    assert frame.height == 0


@pytest.mark.parser
def test_unnamespaced_sbgn_nodes_arcs_compartment_and_dataframe(tmp_path: Path) -> None:
    source = tmp_path / "toy.sbgn"
    source.write_text(VALID_SBGN_NO_NAMESPACE, encoding="utf-8")
    pathway = parse_sbgn(source)
    frame = sbgn_to_df(pathway)
    assert pathway.pathway_id == "toy"
    assert pathway.pathway_name == "process description"
    assert set(pathway.glyphs) == {"g1", "g2"}
    assert set(pathway.compartments) == {"c1"}
    assert len(pathway.arcs) == 1
    assert pathway.arcs[0].spline_points == [
        (50.0, 30.0),
        (65.0, 25.0),
        (80.0, 30.0),
    ]
    assert set(frame["type"]) == {"gene", "compound"}
    assert frame.filter(pl.col("entry_id") == "g1")["x"][0] == 30.0


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-BUG-023: parser locates a namespaced map but searches its glyphs/arcs without namespace"
)
def test_standard_namespaced_sbgn_is_parsed(tmp_path: Path) -> None:
    source = tmp_path / "namespaced.sbgn"
    source.write_text(VALID_SBGN_NAMESPACED, encoding="utf-8")
    pathway = parse_sbgn(source)
    assert set(pathway.glyphs) == {"g1", "g2"}
    assert len(pathway.arcs) == 1
    assert pathway.arcs[0].spline_points[0] == (50.0, 30.0)


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-BUG-024: SBGN namespace is hard-coded to 0.2 and does not accept other valid versions"
)
def test_sbgn_namespace_version_is_discovered_from_document(tmp_path: Path) -> None:
    source = tmp_path / "v03.sbgn"
    source.write_text(
        VALID_SBGN_NAMESPACED.replace("libsbgn/0.2", "libsbgn/0.3"), encoding="utf-8"
    )
    pathway = parse_sbgn(source)
    assert len(pathway.glyphs) == 2
    assert len(pathway.arcs) == 1


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-BUG-025: nested state-variable glyph is also promoted to a top-level biological node"
)
def test_state_variable_is_metadata_not_a_top_level_node(tmp_path: Path) -> None:
    source = tmp_path / "state.sbgn"
    source.write_text(
        """<sbgn><map id="m"><glyph id="protein" class="macromolecule">
        <label text="ERK"/><bbox x="0" y="0" w="40" h="20"/>
        <glyph id="state1" class="state variable" variable="Y" value="P">
          <label text="P@Y"/><bbox x="5" y="-5" w="12" h="8"/>
        </glyph></glyph></map></sbgn>""",
        encoding="utf-8",
    )
    pathway = parse_sbgn(source)
    assert set(pathway.glyphs) == {"protein"}
    assert pathway.glyphs["protein"].state_variables == [
        {"variable": "Y", "value": "P", "label": "P@Y"}
    ]


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-BUG-026: standard <clone/> element is not detected; code checks an attribute instead"
)
def test_standard_sbgn_clone_marker_is_detected(tmp_path: Path) -> None:
    source = tmp_path / "clone.sbgn"
    source.write_text(
        """<sbgn><map id="m"><glyph id="g1" class="macromolecule">
        <label text="TP53"/><clone/><bbox x="0" y="0" w="40" h="20"/>
        </glyph></map></sbgn>""",
        encoding="utf-8",
    )
    assert parse_sbgn(source).glyphs["g1"].clone_marker is True


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-FEATURE-002: SBGNGlyph exposes unit_of_information but parser never populates it"
)
def test_sbgn_unit_of_information_is_parsed(tmp_path: Path) -> None:
    source = tmp_path / "uoi.sbgn"
    source.write_text(
        """<sbgn><map id="m"><glyph id="g1" class="macromolecule">
        <label text="TP53"/><bbox x="0" y="0" w="40" h="20"/>
        <glyph id="u1" class="unit of information"><label text="mt:prot"/></glyph>
        </glyph></map></sbgn>""",
        encoding="utf-8",
    )
    glyph = parse_sbgn(source).glyphs["g1"]
    assert glyph.unit_of_information == [{"label": "mt:prot"}]


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-BUG-027: Bezier control <point> children inside SBGN <next> are discarded"
)
def test_sbgn_arc_control_points_are_preserved(tmp_path: Path) -> None:
    source = tmp_path / "controls.sbgn"
    source.write_text(
        """<sbgn><map id="m">
        <glyph id="a" class="macromolecule"><bbox x="0" y="0" w="10" h="10"/></glyph>
        <glyph id="b" class="macromolecule"><bbox x="50" y="0" w="10" h="10"/></glyph>
        <arc id="e" class="production" source="a" target="b">
          <start x="10" y="5"/><next x="30" y="5"><point x="20" y="20"/><point x="25" y="20"/></next><end x="50" y="5"/>
        </arc></map></sbgn>""",
        encoding="utf-8",
    )
    points = parse_sbgn(source).arcs[0].spline_points
    assert (20.0, 20.0) in points and (25.0, 20.0) in points


@pytest.mark.parser
@pytest.mark.xfail(
    reason="PV-BUG-028: empty SBGN conversion returns a schema-less DataFrame"
)
def test_empty_sbgn_dataframe_has_unified_schema(tmp_path: Path) -> None:
    source = tmp_path / "empty.sbgn"
    source.write_text('<sbgn><map id="empty"/></sbgn>', encoding="utf-8")
    frame = sbgn_to_df(parse_sbgn(source))
    assert "entry_id" in frame.columns
    assert "kegg_names" in frame.columns
    assert frame.height == 0

