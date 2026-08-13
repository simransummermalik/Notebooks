#!/usr/bin/env python3
"""Run the frozen Python half of the R SBGNview comparison.

This script runs offline by default. It uses the SBGN files frozen in the
Pathview Plus v3 checkout and the shared seven-gene, two-condition CSV in this
folder.  All generated evidence is written below ``results/sbgnview``.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


SCRIPT = Path(__file__).resolve()
DAY_ROOT = SCRIPT.parent.parent
WORKSPACE_ROOT = DAY_ROOT.parent
SOURCE_ROOT = DAY_ROOT / "sources" / "pathview-plus"
FIXTURE_ROOT = SOURCE_ROOT / "tests" / "fixtures"
RESULT_ROOT = DAY_ROOT / "results" / "sbgnview"
SHARED_INPUT = DAY_ROOT / "data" / "P00001-shared-control-treatment.csv"

os.environ["PATHVIEW_OFFLINE"] = "1"
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/pathview-plus-sbgn-matplotlib")
sys.path.insert(0, str(SOURCE_ROOT))

import polars as pl  # noqa: E402
import numpy as np  # noqa: E402

import lib as pathview  # noqa: E402
from lib.sbgn_parser import (  # noqa: E402
    arc_resolution_report,
    parse_sbgn,
    sbgn_edges,
    sbgn_to_df,
)
from lib.sbgnview import sbgn_node_map, sbgnview  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(WORKSPACE_ROOT))


def git_commit(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def package_version(distribution: str) -> str:
    return importlib.metadata.version(distribution)


def xml_summary(path: Path) -> dict[str, object]:
    root = ET.parse(path).getroot()
    elements = list(root.iter())
    namespace = ""
    if root.tag.startswith("{"):
        namespace = root.tag[1:].split("}", 1)[0]
    return {
        "xml_namespace": namespace or "none",
        "xml_glyph_elements": sum(local_name(node.tag) == "glyph" for node in elements),
        "xml_arc_elements": sum(local_name(node.tag) == "arc" for node in elements),
    }


def inspect_fixture(name: str, path: Path) -> tuple[dict[str, object], object]:
    pathway = parse_sbgn(path)
    nodes = sbgn_to_df(pathway)
    edges = sbgn_edges(pathway)
    resolution = arc_resolution_report(pathway)
    type_counts = Counter(nodes["type"].to_list()) if nodes.height else Counter()
    metrics: dict[str, object] = {
        "scenario": name,
        "input_file": relative(path),
        "input_sha256": sha256(path),
        **xml_summary(path),
        "primary_glyphs": len(pathway.glyphs),
        "compartments": len(pathway.compartments),
        "parser_arcs": len(pathway.arcs),
        "node_rows": nodes.height,
        "edge_rows": edges.height,
        "gene_nodes": type_counts["gene"],
        "compound_nodes": type_counts["compound"],
        "process_nodes": type_counts["process"],
        "operator_nodes": type_counts["operator"],
        "ports_indexed": len(pathway.ports),
        "state_variables": sum(len(g.state_variables) for g in pathway.glyphs.values()),
        "clone_markers": sum(g.clone_marker for g in pathway.glyphs.values()),
        **resolution,
    }
    return metrics, pathway


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows supplied for {path.name}")
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def output_evidence(path: Path, scenario: str) -> dict[str, object]:
    if not path.exists() or path.stat().st_size == 0:
        raise AssertionError(f"Expected a non-empty output: {path}")
    return {
        "implementation": "Python Pathview Plus",
        "scenario": scenario,
        "format": path.suffix.lstrip(".").upper(),
        "output_file": relative(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> None:
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)

    fixtures = {
        "P00001 bare XML": FIXTURE_ROOT / "P00001.new.layout.sbgn",
        "P00001 default namespace": FIXTURE_ROOT / "P00001.namespaced.sbgn",
        "ports, state, and clone fixture": FIXTURE_ROOT / "ports_pd.sbgn",
    }
    for path in [*fixtures.values(), SHARED_INPUT]:
        if not path.is_file():
            raise FileNotFoundError(path)

    metric_rows: list[dict[str, object]] = []
    parsed: dict[str, object] = {}
    for scenario, path in fixtures.items():
        metrics, pathway = inspect_fixture(scenario, path)
        metric_rows.append(metrics)
        parsed[scenario] = pathway

    bare = parsed["P00001 bare XML"]
    namespaced = parsed["P00001 default namespace"]
    ports = parsed["ports, state, and clone fixture"]

    bare_ids = list(bare.glyphs)  # type: ignore[attr-defined]
    namespaced_ids = list(namespaced.glyphs)  # type: ignore[attr-defined]
    bare_arcs = [
        (a.arc_id, a.arc_class, a.source, a.target, a.spline_points)
        for a in bare.arcs  # type: ignore[attr-defined]
    ]
    namespaced_arcs = [
        (a.arc_id, a.arc_class, a.source, a.target, a.spline_points)
        for a in namespaced.arcs  # type: ignore[attr-defined]
    ]
    assert bare_ids == namespaced_ids
    assert bare_arcs == namespaced_arcs
    assert len(bare.glyphs) == 76 and len(bare.compartments) == 2  # type: ignore[attr-defined]
    assert len(bare.arcs) == 83 and len(bare.resolved_arcs) == 83  # type: ignore[attr-defined]
    assert len(ports.glyphs) == 4 and len(ports.compartments) == 1  # type: ignore[attr-defined]
    ports_report = arc_resolution_report(ports)  # type: ignore[arg-type]
    assert ports_report == {
        "arcs_total": 3,
        "arcs_resolved": 3,
        "arcs_via_port": 2,
        "ports_indexed": 2,
        "resolution_rate": 1.0,
    }
    assert sum(len(g.state_variables) for g in ports.glyphs.values()) == 1  # type: ignore[attr-defined]
    assert sum(g.clone_marker for g in ports.glyphs.values()) == 1  # type: ignore[attr-defined]

    shared = pl.read_csv(SHARED_INPUT)
    expected = pl.DataFrame(
        {
            "symbol": ["COMT", "DDC", "TH", "DBH", "PNMT", "SLC18A2", "SLC6A3"],
            "Control": [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5],
            "Treatment": [1.5, 1.0, 0.5, 0.0, -0.5, -1.0, -1.5],
        }
    )
    assert shared.equals(expected)

    bare_nodes = sbgn_to_df(bare)  # type: ignore[arg-type]
    mapping = sbgn_node_map(shared, bare_nodes, id_type="SYMBOL", detailed=True)
    assert mapping.ok and mapping.data is not None
    assert mapping.n_nodes == 28
    assert mapping.n_nodes_with_data == 9
    assert mapping.n_ids_input == 7 and mapping.n_ids_mapped == 7
    assert mapping.value_columns == ["Control", "Treatment"]

    mapped = mapping.data.filter(
        pl.any_horizontal(
            pl.col("Control").is_not_null(),
            pl.col("Treatment").is_not_null(),
        )
    ).select(
        "entry_id",
        "label",
        "glyph_class",
        "type",
        "kegg_names",
        "Control",
        "Treatment",
    )
    assert mapped.height == 9
    mapped.with_columns(
        pl.col("kegg_names").list.join(";").alias("kegg_names")
    ).write_csv(RESULT_ROOT / "python-mapped-nodes.tsv", separator="\t")

    output_rows: list[dict[str, object]] = []
    color_rows: list[dict[str, object]] = []
    bare_svg_result = None
    for output_format in ("svg", "png"):
        result = sbgnview(
            fixtures["P00001 bare XML"],
            gene_data=shared,
            gene_idtype="SYMBOL",
            out_dir=RESULT_ROOT,
            out_suffix="python-two-state",
            output_format=output_format,
            title="P00001: Control and Treatment",
            subtitle="The two vertical halves are the two condition columns",
            plot_col_key=True,
            new_signature=True,
            quiet=True,
        )
        assert result.output_path is not None
        output_rows.append(output_evidence(Path(result.output_path), "shared two-state mapping"))
        if output_format == "svg":
            bare_svg_result = result
            assert result.cols_gene is not None
            colour_columns = [c for c in result.cols_gene.columns if c.endswith("_col")]
            assert colour_columns == ["Control_col", "Treatment_col"]
            colours = result.cols_gene.filter(
                pl.col("id").is_in(mapped["entry_id"].to_list())
            ).select("id", *colour_columns)
            assert colours.height == 9
            for row in colours.iter_rows(named=True):
                color_rows.append(
                    {
                        "entry_id": row["id"],
                        "Control_color": row["Control_col"],
                        "Treatment_color": row["Treatment_col"],
                    }
                )

    namespaced_result = sbgnview(
        fixtures["P00001 default namespace"],
        gene_data=shared,
        gene_idtype="SYMBOL",
        out_dir=RESULT_ROOT,
        out_suffix="python-two-state",
        output_format="svg",
        title="P00001: Control and Treatment",
        subtitle="The two vertical halves are the two condition columns",
        plot_col_key=True,
        new_signature=True,
        quiet=True,
    )
    assert namespaced_result.output_path is not None
    assert bare_svg_result is not None
    assert namespaced_result.node_data.equals(bare_svg_result.node_data)
    assert namespaced_result.edge_data.equals(bare_svg_result.edge_data)
    assert namespaced_result.plot_data_gene.equals(bare_svg_result.plot_data_gene)
    assert namespaced_result.frame is not None and bare_svg_result.frame is not None
    assert np.array_equal(namespaced_result.frame.array, bare_svg_result.frame.array)
    output_rows.append(
        output_evidence(Path(namespaced_result.output_path), "namespaced shared two-state mapping")
    )

    structural = sbgnview(
        fixtures["ports, state, and clone fixture"],
        out_dir=RESULT_ROOT,
        out_suffix="python-structural",
        output_format="svg",
        title="Small SBGN structural fixture",
        plot_col_key=False,
        new_signature=True,
        quiet=True,
    )
    assert structural.output_path is not None
    output_rows.append(output_evidence(Path(structural.output_path), "ports/state/clone fixture"))

    write_tsv(RESULT_ROOT / "python-metrics.tsv", metric_rows)
    write_tsv(RESULT_ROOT / "python-node-colors.tsv", color_rows)
    write_tsv(RESULT_ROOT / "output-manifest-python.tsv", output_rows)

    report = {
        "title": "Python Pathview Plus SBGN frozen comparison evidence",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "offline": True,
        "environment": {
            "python": platform.python_version(),
            "pathview_plus": pathview.__version__,
            "pathview_plus_distribution": package_version("pathview-plus"),
            "pathview_plus_commit": git_commit(SOURCE_ROOT),
            "polars": package_version("polars"),
            "numpy": package_version("numpy"),
            "matplotlib": package_version("matplotlib"),
            "pillow": package_version("pillow"),
            "platform": platform.platform(),
        },
        "shared_input": {
            "file": relative(SHARED_INPUT),
            "sha256": sha256(SHARED_INPUT),
            "ids": shared["symbol"].to_list(),
            "conditions": ["Control", "Treatment"],
            "rows": shared.to_dicts(),
        },
        "fixtures": metric_rows,
        "namespace_parity": {
            "passed": True,
            "same_primary_glyph_ids_in_order": True,
            "same_arc_ids_classes_endpoints_and_points_in_order": True,
            "same_mapped_node_and_edge_tables": True,
            "same_rendered_raster_frame": True,
        },
        "mapping": {
            "summary": mapping.summary(),
            "nodes_with_data": mapping.n_nodes_with_data,
            "eligible_gene_nodes": mapping.n_nodes,
            "input_ids_used": mapping.n_ids_mapped,
            "input_ids_total": mapping.n_ids_input,
            "value_columns": mapping.value_columns,
            "mapped_node_rows": mapped.to_dicts(),
            "two_vertical_color_bands_confirmed": True,
        },
        "outputs": output_rows,
        "assertions": {
            "P00001_bare_and_namespaced_identical": True,
            "P00001_bare_and_namespaced_render_frames_identical": True,
            "P00001_83_of_83_arcs_resolved": True,
            "ports_fixture_3_of_3_arcs_resolved": True,
            "ports_fixture_2_arcs_resolved_through_ports": True,
            "ports_fixture_state_variable_captured": True,
            "ports_fixture_clone_marker_captured": True,
            "shared_mapping_9_of_28_nodes": True,
            "shared_mapping_7_of_7_input_ids": True,
            "two_condition_color_columns": True,
            "all_outputs_nonempty": True,
        },
    }
    with (RESULT_ROOT / "python-comparison.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")

    print("PASS: Python Pathview Plus SBGN comparison")
    print(f"  namespace parity: 76 primary glyphs + 2 compartments, 83 arcs")
    print(f"  shared mapping: {mapping.summary()}")
    print("  ports fixture: 3/3 arcs, 2 via ports, 1 state variable, 1 clone marker")
    for row in output_rows:
        print(f"  wrote {row['output_file']} ({row['bytes']} bytes)")


if __name__ == "__main__":
    main()
