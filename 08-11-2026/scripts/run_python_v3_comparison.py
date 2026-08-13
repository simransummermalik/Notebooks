#!/usr/bin/env python3
"""Run my controlled Pathview Plus v3 checks for the August 11 comparison.

This stays offline and uses the frozen KEGG and SBGN files from the exact
Pathview Plus commit being tested. It writes figures, flat tables, and
machine-readable evidence under ``results/python-pathview``.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path
from xml.etree import ElementTree as ET

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import polars as pl
from PIL import Image, ImageChops, ImageDraw

import pathview as pv


DAY_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = DAY_ROOT.parent
SOURCE = DAY_ROOT / "sources" / "pathview-plus"
FIXTURES = SOURCE / "tests" / "fixtures"
DATA = DAY_ROOT / "data"
RESULTS = DAY_ROOT / "results" / "python-pathview"
FIGURES = RESULTS / "figures"
TABLES = RESULTS / "tables"
CLI_RESULTS = RESULTS / "cli"

for directory in (RESULTS, FIGURES, TABLES, CLI_RESULTS):
    directory.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("PATHVIEW_CACHE", str(DAY_ROOT / "cache" / "pathview-plus"))
os.environ.setdefault("XDG_CACHE_HOME", str(DAY_ROOT / "cache"))
os.environ.setdefault("MPLCONFIGDIR", str(DAY_ROOT / "cache" / "matplotlib"))

pv.set_offline(True)


def relative(path: str | Path) -> str:
    """Write paths from the workspace root so the JSON is portable."""
    path = Path(path).resolve()
    try:
        return str(path.relative_to(WORKSPACE_ROOT.resolve()))
    except ValueError:
        return str(path)


def digest(path: str | Path, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_evidence(path: str | Path) -> dict:
    path = Path(path)
    item: dict = {"path": relative(path), "exists": path.exists()}
    if not path.exists():
        return item
    item.update({"bytes": path.stat().st_size, "sha256": digest(path)})
    if path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        with Image.open(path) as image:
            item.update({"width_px": image.width, "height_px": image.height,
                         "mode": image.mode})
    return item


REPORT: dict = {
    "title": "My controlled Pathview Plus v3 comparison",
    "run_date": "2026-08-11",
    "offline": True,
    "checks": [],
    "outputs": [],
    "observations": [],
}


def remember_output(path: str | Path, purpose: str) -> dict:
    item = file_evidence(path)
    item["purpose"] = purpose
    REPORT["outputs"].append(item)
    return item


def record_check(name: str, status: str, seconds: float, details=None, error=None):
    item = {
        "id": f"PY{len(REPORT['checks']) + 1:02d}",
        "name": name,
        "status": status,
        "seconds": round(seconds, 4),
    }
    if details is not None:
        item["details"] = details
    if error is not None:
        item["error"] = error
    REPORT["checks"].append(item)
    suffix = f": {error}" if error else ""
    print(f"{status.upper()} {item['id']} {name}{suffix}")
    return item


def check(name):
    def decorator(function):
        started = time.perf_counter()
        try:
            details = function()
            record_check(name, "pass", time.perf_counter() - started, details=details)
        except Exception as exc:  # keep running so one problem cannot hide later checks
            record_check(
                name,
                "fail",
                time.perf_counter() - started,
                error=f"{type(exc).__name__}: {exc}",
                details={"traceback": traceback.format_exc(limit=6)},
            )
        return function
    return decorator


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def color_mask(image: np.ndarray, hex_color: str, tolerance: int = 45) -> np.ndarray:
    rgb = np.array([int(hex_color[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.int16)
    pixels = image[..., :3].astype(np.int16)
    return np.all(np.abs(pixels - rgb) <= tolerance, axis=2)


def color_count(image: np.ndarray, hex_color: str, tolerance: int = 45) -> int:
    return int(color_mask(image, hex_color, tolerance).sum())


def mapped_rows(frame: pl.DataFrame, identifier: str) -> pl.DataFrame:
    rows = []
    for row in frame.iter_rows(named=True):
        ids = {part.strip() for part in str(row.get("all_mapped") or "").split(",")}
        if identifier in ids:
            rows.append(row)
    return pl.DataFrame(rows, schema=frame.schema) if rows else frame.head(0)


def crop_node(result, row: dict, destination: Path, padding: int = 1) -> np.ndarray:
    image = result.image_array
    require(image is not None, "The result did not carry a raw map raster")
    x, y = float(row["x"]), float(row["y"])
    width, height = float(row["width"]), float(row["height"])
    x0 = max(0, int(np.floor(x - width / 2)) - padding)
    x1 = min(image.shape[1], int(np.ceil(x + width / 2)) + padding)
    y0 = max(0, int(np.floor(y - height / 2)) - padding)
    y1 = min(image.shape[0], int(np.ceil(y + height / 2)) + padding)
    crop = image[y0:y1, x0:x1, :3]
    Image.fromarray(crop).save(destination)
    remember_output(destination, "Close crop used to prove the state-band order")
    return crop


def split_vertical(image: np.ndarray, pieces: int) -> list[np.ndarray]:
    edges = np.linspace(0, image.shape[1], pieces + 1).astype(int)
    return [image[:, edges[i]:edges[i + 1], :] for i in range(pieces)]


def contact_sheet(left_path: Path, right_path: Path, destination: Path,
                  left_label: str, right_label: str) -> Path:
    with Image.open(left_path).convert("RGB") as left, Image.open(right_path).convert("RGB") as right:
        target_h = min(left.height, right.height)
        if left.height != target_h:
            left = left.resize((round(left.width * target_h / left.height), target_h))
        if right.height != target_h:
            right = right.resize((round(right.width * target_h / right.height), target_h))
        label_h = 34
        sheet = Image.new("RGB", (left.width + right.width, target_h + label_h), "white")
        sheet.paste(left, (0, label_h))
        sheet.paste(right, (left.width, label_h))
        draw = ImageDraw.Draw(sheet)
        draw.text((10, 10), left_label, fill="black")
        draw.text((left.width + 10, 10), right_label, fill="black")
        sheet.save(destination)
    remember_output(destination, "Side-by-side R and Python comparison")
    return destination


def raster_difference(left_path: Path, right_path: Path, destination: Path) -> dict:
    with Image.open(left_path).convert("RGB") as left, Image.open(right_path).convert("RGB") as right:
        require(left.size == right.size, f"Raster dimensions differ: {left.size} and {right.size}")
        a, b = np.asarray(left), np.asarray(right)
        delta = np.abs(a.astype(np.int16) - b.astype(np.int16))
        changed = np.any(delta > 0, axis=2)
        amplified = np.clip(delta * 4, 0, 255).astype(np.uint8)
        Image.fromarray(amplified).save(destination)
    remember_output(destination, "Amplified absolute pixel difference (black means identical)")
    return {
        "same_dimensions": True,
        "changed_pixel_fraction": round(float(changed.mean()), 6),
        "mean_absolute_channel_difference": round(float(delta.mean()), 4),
        "maximum_channel_difference": int(delta.max()),
    }


def save_frame_csv(frame: pl.DataFrame | None, destination: Path, purpose: str):
    require(frame is not None, f"No table was returned for {purpose}")
    # KGML/SBGN identifier columns are lists. CSV has no native list type, so
    # I flatten those cells with semicolons instead of losing the table.
    expressions = []
    for name, dtype in frame.schema.items():
        if isinstance(dtype, pl.List):
            expressions.append(
                pl.col(name).list.eval(pl.element().cast(pl.String)).list.join(";").alias(name)
            )
        elif dtype.is_nested():
            expressions.append(pl.col(name).cast(pl.String).alias(name))
    flat = frame.with_columns(expressions) if expressions else frame
    flat.write_csv(destination)
    remember_output(destination, purpose)


GENE_SCALE = pv.ColorScale(
    limit=2.0, bins=11, low="#00FF00", mid="#BEBEBE", high="#FF0000",
    label="Gene log2 fold change",
)
CPD_SCALE = pv.ColorScale(
    limit=2.0, bins=11, low="#0000FF", mid="#BEBEBE", high="#FFFF00",
    label="Compound log2 fold change",
)


def native_call(data: pl.DataFrame, suffix: str):
    return pv.pathview(
        "04110", gene_data=data, species="hsa", kegg_dir=FIXTURES,
        out_dir=FIGURES, out_suffix=suffix, render_mode="native",
        output_format="png", gene_color=GENE_SCALE, map_symbol=False,
        plot_col_key=False, new_signature=False, quiet=True,
    )


@check("environment, exact version, and pinned source commit")
def _environment():
    commit = subprocess.check_output(
        ["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True
    ).strip()
    status = subprocess.check_output(
        ["git", "-C", str(SOURCE), "status", "--short"], text=True
    ).strip()
    require(pv.__version__ == "3.1.0", f"Expected 3.1.0, got {pv.__version__}")
    require(commit == "d4d45decec56e1ebec15cf04ae62ff944851780e",
            f"Unexpected source commit {commit}")
    require(not status, "The cloned upstream source has local changes")
    environment = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "pathview_plus": pv.__version__,
        "commit": commit,
        "source_clean": True,
    }
    REPORT["environment"] = environment
    return environment


@check("saved upstream test result")
def _upstream_result():
    junit = DAY_ROOT / "results" / "pathview-plus-v3-upstream-junit.xml"
    root = ET.parse(junit).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    totals = {
        key: sum(int(s.attrib.get(key, 0)) for s in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    totals["passed"] = totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
    totals["junit"] = relative(junit)
    require(totals == {**totals, "tests": 327, "failures": 0, "errors": 0,
                       "skipped": 6, "passed": 321}, "Unexpected upstream JUnit totals")
    return totals


@check("frozen R and Python pathway inputs are byte-for-byte identical")
def _fixture_identity():
    pairs = []
    r_cache = DAY_ROOT / "results" / "r-pathview" / "cache"
    for name in ("hsa04110.xml", "hsa04110.png"):
        python_file, r_file = FIXTURES / name, r_cache / name
        require(r_file.exists(), f"R comparison fixture is missing: {r_file}")
        same = digest(python_file) == digest(r_file)
        require(same, f"R and Python used different {name} files")
        pairs.append({"name": name, "same_sha256": same,
                      "sha256": digest(python_file)})
    return {"pairs": pairs}


@check("KEGG KGML parsing and pathway edges")
def _kgml_parse():
    pathway = pv.parse_kgml(FIXTURES / "hsa04110.xml")
    nodes = pv.node_info(pathway)
    edges = pv.pathway_edges(pathway)
    tca_edges = pv.pathway_edges(pv.parse_kgml(FIXTURES / "hsa00020.xml"))
    require(nodes.height == 115, f"Expected 115 nodes, got {nodes.height}")
    require(edges.height == 79, f"Expected 79 edges, got {edges.height}")
    kinds = sorted(set(edges["source_kind"].to_list()) | set(tca_edges["source_kind"].to_list()))
    require({"relation", "reaction"}.issubset(kinds),
            "The two controlled KGML files did not collectively contain relation and reaction edges")
    save_frame_csv(nodes, TABLES / "hsa04110-python-nodes.csv", "Parsed Python KEGG node table")
    save_frame_csv(edges, TABLES / "hsa04110-python-edges.csv", "Parsed Python KEGG edge table")
    return {"hsa04110_nodes": nodes.height, "hsa04110_edges": edges.height,
            "hsa00020_edges": tca_edges.height, "edge_sources_across_fixtures": kinds}


STATE_RESULTS: dict[str, object] = {}


@check("one-, two-, and three-state native rendering")
def _native_states():
    strong = pl.read_csv(DATA / "hsa04110-strong-three-state.csv")
    cases = {
        "one-state": strong.select("entrez", "Low"),
        "half-half": strong.select("entrez", "Low", "High"),
        "three-state": strong,
    }
    details = {}
    for label, frame in cases.items():
        result = native_call(frame, f"python-{label}-figure")
        STATE_RESULTS[label] = result
        remember_output(result.output_path, f"Pathview Plus {label} composed native figure")
        raw = FIGURES / f"hsa04110.python-{label}.raw.png"
        result.save(raw)
        raw_info = remember_output(raw, f"Pathview Plus {label} raw KEGG-sized map")
        require((raw_info["width_px"], raw_info["height_px"]) == (1039, 801),
                f"{label} raw map changed the 1039 x 801 source dimensions")

        hit = mapped_rows(result.plot_data_gene, "1029")
        require(hit.height >= 1, f"Entrez 1029 did not map in {label}")
        row = hit.row(0, named=True)
        crop_path = FIGURES / f"hsa04110.python-{label}.CDKN2A-crop.png"
        crop = crop_node(result, row, crop_path)
        pieces = split_vertical(crop, frame.width - 1)
        expected = ["#00FF00"] if label == "one-state" else (
            ["#00FF00", "#FF0000"] if label == "half-half"
            else ["#00FF00", "#BEBEBE", "#FF0000"]
        )
        counts = []
        for piece, color in zip(pieces, expected):
            target = color_count(piece, color)
            other = max(color_count(piece, other_color) for other_color in expected if other_color != color) \
                if len(expected) > 1 else 0
            require(target > other and target > 0,
                    f"{label} did not keep the expected left-to-right state order")
            counts.append({"expected": color, "target_pixels": target,
                           "largest_other_color_pixels": other})
        details[label] = {
            "states_in_order": frame.columns[1:],
            "mapped_gene_diagnostic": result.diagnostics.get("gene"),
            "CDKN2A_geometry": {key: row[key] for key in ("x", "y", "width", "height")},
            "band_color_counts": counts,
            "raw_output": raw_info,
        }
    return details


@check("same Control/Treatment dataset in Python and R Pathview")
def _shared_r_python():
    shared = pl.read_csv(DATA / "hsa04110-shared-control-treatment.csv")
    result = native_call(shared, "python-shared-control-treatment-figure")
    STATE_RESULTS["shared"] = result
    remember_output(result.output_path, "Pathview Plus shared-dataset composed native figure")
    python_raw = FIGURES / "hsa04110.python-shared-control-treatment.raw.png"
    result.save(python_raw)
    remember_output(python_raw, "Pathview Plus shared-dataset raw KEGG-sized map")

    requested = {str(value) for value in shared["entrez"].to_list()}
    used = set()
    selected = []
    for row in result.plot_data_gene.iter_rows(named=True):
        # all_mapped is comma-delimited; splitting directly avoids regex assumptions.
        row_ids = {part.strip() for part in str(row.get("all_mapped") or "").split(",") if part.strip()}
        if row_ids & requested:
            used |= row_ids & requested
            selected.append(row)
    require(used == requested, f"Not every shared ID mapped: missing {sorted(requested - used)}")
    selected_frame = pl.DataFrame(selected, schema=result.plot_data_gene.schema)
    save_frame_csv(selected_frame, TABLES / "hsa04110.python-shared-selected-nodes.csv",
                   "Python nodes selected by the exact shared dataset")

    r_raw = DAY_ROOT / "results" / "r-pathview" / "hsa04110.r-shared-control-treatment.multi.png"
    sheet = FIGURES / "hsa04110.R-vs-Python.shared-side-by-side.png"
    diff = FIGURES / "hsa04110.R-vs-Python.shared-pixel-difference.png"
    contact_sheet(r_raw, python_raw, sheet, "R pathview 1.52.0", "Pathview Plus 3.1.0")
    difference = raster_difference(r_raw, python_raw, diff)
    return {
        "same_input_csv": relative(DATA / "hsa04110-shared-control-treatment.csv"),
        "requested_ids": sorted(requested),
        "used_ids": sorted(used),
        "python_nodes_with_data": selected_frame.height,
        "python_mapping": result.diagnostics.get("gene"),
        "r_output": file_evidence(r_raw),
        "python_output": file_evidence(python_raw),
        "pixel_comparison": difference,
        "interpretation": "The dimensions and pathway coordinates are directly comparable; styling and node aggregation can still differ.",
    }


@check("native, vector, SVG, PDF, graph, and automatic render modes")
def _render_modes():
    shared = pl.read_csv(DATA / "hsa04110-shared-control-treatment.csv")
    cases = [
        ("vector", "png"),
        ("vector", "pdf"),
        ("svg", "svg"),
        ("graph", "png"),
        ("auto", "png"),
    ]
    outputs = []
    for mode, output_format in cases:
        suffix = f"python-mode-{mode}-{output_format}"
        result = pv.pathview(
            "04110", gene_data=shared, species="human", kegg_dir=FIXTURES,
            out_dir=FIGURES, out_suffix=suffix, render_mode=mode,
            output_format=output_format, gene_color=GENE_SCALE,
            map_symbol=False, plot_col_key=False, new_signature=False,
            quiet=True,
        )
        evidence = remember_output(result.output_path, f"{mode} / {output_format} rendering check")
        require(evidence["bytes"] > 1_000, f"{mode}/{output_format} output was unexpectedly small")
        if output_format == "pdf":
            require(Path(result.output_path).read_bytes().startswith(b"%PDF"), "PDF signature is missing")
        if output_format == "svg":
            ET.parse(result.output_path)
            require('class="pv-edge"' in Path(result.output_path).read_text(), "Standalone SVG has no pathway edges")
        outputs.append({**evidence, "render_mode": mode, "format": output_format})
    return {"outputs": outputs}


@check("genes and compounds together with separate scales")
def _dual_omics():
    genes = pl.read_csv(DATA / "hsa00020-dual-omics-genes.csv")
    compounds = pl.read_csv(DATA / "hsa00020-dual-omics-compounds.csv")
    r_cache = DAY_ROOT / "results" / "r-pathview" / "cache"
    result = pv.pathview(
        "00020", gene_data=genes, cpd_data=compounds, species="hsa",
        kegg_dir=r_cache, out_dir=FIGURES, out_suffix="python-gene-compound-figure",
        render_mode="native", output_format="png", gene_color=GENE_SCALE,
        cpd_color=CPD_SCALE, map_symbol=False, map_cpd_name=False,
        plot_col_key=False, new_signature=False, quiet=True,
    )
    remember_output(result.output_path, "Pathview Plus gene-and-compound composed figure")
    raw = FIGURES / "hsa00020.python-gene-compound.raw.png"
    result.save(raw)
    remember_output(raw, "Pathview Plus gene-and-compound raw map")
    require(result.plot_data_gene is not None and result.plot_data_cpd is not None,
            "One of the two omics tables was not returned")
    gene_rows = result.plot_data_gene.filter(pl.col("Low").is_not_null()).height
    cpd_rows = result.plot_data_cpd.filter(pl.col("Low").is_not_null()).height
    require(gene_rows > 0 and cpd_rows > 0, "Gene or compound values did not land on hsa00020")
    save_frame_csv(result.plot_data_gene, TABLES / "hsa00020.python-gene-nodes.csv",
                   "Python dual-omics gene-node table")
    save_frame_csv(result.plot_data_cpd, TABLES / "hsa00020.python-compound-nodes.csv",
                   "Python dual-omics compound-node table")

    c00022 = mapped_rows(result.plot_data_cpd, "C00022")
    require(c00022.height >= 1, "C00022 did not map")
    row = c00022.row(0, named=True)
    crop = crop_node(result, row, FIGURES / "hsa00020.python-C00022-crop.png", padding=3)
    r_raw = DAY_ROOT / "results" / "r-pathview" / "hsa00020.r-gene-compound.multi.png"
    sheet = FIGURES / "hsa00020.R-vs-Python.dual-omics-side-by-side.png"
    contact_sheet(r_raw, raw, sheet, "R pathview 1.52.0", "Pathview Plus 3.1.0")

    vector = pv.pathview(
        "00020", gene_data=genes, cpd_data=compounds, species="hsa",
        kegg_dir=FIXTURES, out_dir=FIGURES, out_suffix="python-gene-compound-vector",
        render_mode="vector", output_format="png", gene_color=GENE_SCALE,
        cpd_color=CPD_SCALE, map_symbol=False, map_cpd_name=False, quiet=True,
    )
    remember_output(vector.output_path, "Pathview Plus dual-omics vector map with separate keys")
    return {
        "gene_nodes_with_data": gene_rows,
        "compound_nodes_with_data": cpd_rows,
        "gene_diagnostic": result.diagnostics.get("gene"),
        "compound_diagnostic": result.diagnostics.get("cpd"),
        "C00022_geometry": {key: row[key] for key in ("x", "y", "width", "height")},
        "C00022_crop_shape": list(crop.shape),
        "note": "The KGML width/height are treated as the full compound diameter in v3.",
    }


@check("namespaced SBGN parsing, ports, arcs, and compartments")
def _sbgn_parse():
    plain = pv.parse_sbgn(FIXTURES / "P00001.new.layout.sbgn")
    namespaced = pv.parse_sbgn(FIXTURES / "P00001.namespaced.sbgn")
    require(len(plain.glyphs) == len(namespaced.glyphs) == 76, "Namespaced glyph count changed")
    require(len(plain.arcs) == len(namespaced.arcs) == 83, "Namespaced arc count changed")
    port_pathway = pv.parse_sbgn(FIXTURES / "ports_pd.sbgn")
    port_report = pv.arc_resolution_report(port_pathway)
    require(port_report["resolution_rate"] == 1.0, "Not every port-based arc resolved")
    require(port_report["arcs_via_port"] >= 2, "The port-resolution fixture did not use ports")
    nodes = pv.sbgn_to_df(namespaced)
    edges = pv.sbgn_edges(namespaced)
    compartments = pv.sbgn_compartments(namespaced)
    save_frame_csv(nodes, TABLES / "P00001.python-sbgn-nodes.csv", "Parsed Python SBGN glyph table")
    save_frame_csv(edges, TABLES / "P00001.python-sbgn-edges.csv", "Parsed Python SBGN arc table")
    return {
        "glyphs": len(namespaced.glyphs), "arcs": len(namespaced.arcs),
        "node_rows": nodes.height, "edge_rows": edges.height,
        "compartments": compartments.height, "port_fixture": port_report,
    }


@check("mapped two-state SBGN rendering to PNG, PDF, and SVG")
def _sbgn_render():
    genes = pl.read_csv(DATA / "P00001-shared-control-treatment.csv")
    outputs = []
    first = None
    for output_format in ("png", "pdf", "svg"):
        result = pv.sbgnview(
            FIXTURES / "P00001.new.layout.sbgn", gene_data=genes,
            gene_idtype="SYMBOL", out_dir=FIGURES,
            out_suffix=f"python-two-state-{output_format}",
            output_format=output_format, gene_color=GENE_SCALE,
            show_compartments=True, quiet=True,
        )
        first = first or result
        evidence = remember_output(result.output_path, f"Mapped SBGN {output_format.upper()} output")
        require(evidence["bytes"] > 1_000, f"SBGN {output_format} output was unexpectedly small")
        if output_format == "pdf":
            require(Path(result.output_path).read_bytes().startswith(b"%PDF"), "SBGN PDF signature is missing")
        if output_format == "svg":
            ET.parse(result.output_path)
        outputs.append(evidence)
    require(first is not None and first.plot_data_gene is not None, "SBGN gene table was not returned")
    with_data = first.plot_data_gene.filter(pl.col("Control").is_not_null()).height
    require(with_data == 9, f"Expected 9 mapped SBGN glyph rows, got {with_data}")
    require(first.diagnostics["compartments"] == 2, "The two compartments were not kept")
    save_frame_csv(first.plot_data_gene, TABLES / "P00001.python-mapped-gene-glyphs.csv",
                   "Python SBGN mapped-gene table")
    raw = FIGURES / "P00001.python-two-state.raw.png"
    first.save(raw)
    remember_output(raw, "Mapped SBGN raw pathway raster")
    return {"mapped_glyph_rows": with_data, "diagnostics": first.diagnostics,
            "outputs": outputs}


@check("offline SBGN collection index and identifier crosswalks")
def _sbgn_collection():
    info = pv.sbgn_collection_info()
    require(info["total"] == 5206, f"Expected 5,206 indexed pathways, got {info['total']}")
    require(set(info["by_source"]) == {"reactome", "smpdb", "panther", "metacyc", "metacrop"},
            "The collection does not contain all five declared sources")
    route = pv.id_route("ENTREZ", "SYMBOL")
    mapped = pv.map_ids_to_sbgn(["1017", "7157"], "ENTREZ", "SYMBOL")
    require(mapped["SYMBOL"].to_list() == ["CDK2", "TP53"], "Known Entrez-to-symbol mapping changed")
    index = pv.list_sbgn_pathways("panther")
    require(index.height > 100, "PANTHER index is unexpectedly small")
    return {"collection": info, "entrez_to_symbol_route": route,
            "known_mapping": mapped.to_dicts(), "panther_rows": index.height}


@check("batch rendering and partial-failure reporting")
def _batch():
    genes = pl.read_csv(DATA / "hsa04110-shared-control-treatment.csv")
    result_set = pv.pathview(
        ["00020", "99999", "04110"], gene_data=genes, species="hsa",
        kegg_dir=FIXTURES, out_dir=FIGURES, out_suffix="python-batch",
        render_mode="vector", gene_color=GENE_SCALE, map_symbol=False,
        plot_col_key=False, new_signature=False, quiet=True,
    )
    require(isinstance(result_set, pv.PathwayResultSet), "Batch did not return PathwayResultSet")
    require(len(result_set) == 2, f"Expected two successful pathways, got {len(result_set)}")
    require("99999" in result_set.failures, "Missing pathway was not recorded as a failure")
    batch_table = result_set.to_frame()
    save_frame_csv(batch_table, TABLES / "python-batch-results.csv", "Batch status table")
    for output in result_set.output_paths:
        remember_output(output, "Successful member of the Python batch render")
    return {"rendered": len(result_set), "failed": result_set.failures,
            "summary": result_set.summary()}


@check("highlighting is visible, composable, and leaves the original unchanged")
def _highlighting():
    base = STATE_RESULTS.get("half-half")
    require(base is not None, "The two-state result was not available")
    before = base.image_array.copy()
    highlighted = (
        base
        + pv.highlight_nodes(["1029", "7157"], color="#7C3AED", width=4)
        + pv.highlight_path(["1029", "7157"], color="#F59E0B",
                            node_width=3, edge_width=3)
        + pv.change_labels({"1029": "CDKN2A *"})
    )
    require(np.array_equal(before, base.image_array), "Composing highlights changed the original result")
    require(not np.array_equal(before, highlighted.image_array), "The highlight made no visible pixel change")
    output = FIGURES / "hsa04110.python-highlighted.png"
    highlighted.save(output)
    remember_output(output, "Composable highlighted Pathview Plus map")
    return {"modifiers": len(highlighted.modifications),
            "changed_pixels": int(np.any(before != highlighted.image_array, axis=2).sum()),
            "original_unchanged": True}


@check("group splitting and multi-gene node expansion")
def _expansion():
    genes = pl.read_csv(DATA / "hsa04110-shared-control-treatment.csv")
    plain = pv.pathview(
        "04110", gene_data=genes, species="hsa", kegg_dir=FIXTURES,
        out_dir=FIGURES, out_suffix="python-unexpanded", render_mode="vector",
        gene_color=GENE_SCALE, map_symbol=False, plot_col_key=False,
        new_signature=False, quiet=True,
    )
    expanded = pv.pathview(
        "04110", gene_data=genes, species="hsa", kegg_dir=FIXTURES,
        out_dir=FIGURES, out_suffix="python-expanded", render_mode="vector",
        gene_color=GENE_SCALE, map_symbol=False, plot_col_key=False,
        new_signature=False, split_group=True, expand_node=True, quiet=True,
    )
    require(expanded.node_data.height > plain.node_data.height,
            "Splitting/expansion did not add the expected sub-nodes")
    ids = set(expanded.node_data["entry_id"].to_list())
    require(set(expanded.edge_data["source"].to_list()) <= ids, "An expanded edge source points to a missing node")
    require(set(expanded.edge_data["target"].to_list()) <= ids, "An expanded edge target points to a missing node")
    remember_output(plain.output_path, "Unexpanded Pathview Plus vector comparison")
    remember_output(expanded.output_path, "Split-group and expanded-node Pathview Plus vector comparison")
    return {"plain_nodes": plain.node_data.height,
            "expanded_nodes": expanded.node_data.height,
            "expanded_edges": expanded.edge_data.height,
            "diagnostic": expanded.diagnostics.get("expansion")}


@check("command-line interface and bundled smoke test")
def _cli():
    executable = Path(sys.executable).parent / "pathview-plus"
    environment = dict(os.environ)
    environment.update({"PATHVIEW_CACHE": str(DAY_ROOT / "cache" / "pathview-plus"),
                        "XDG_CACHE_HOME": str(DAY_ROOT / "cache"),
                        "MPLBACKEND": "Agg"})

    def command(arguments):
        completed = subprocess.run(
            [str(executable), *map(str, arguments)], cwd=WORKSPACE_ROOT,
            env=environment, text=True, capture_output=True, timeout=90,
        )
        require(completed.returncode == 0,
                f"CLI command failed ({completed.returncode}): {completed.stderr.strip()}")
        return completed.stdout.strip()

    version = command(["--version"])
    species = command(["species", "human"])
    parity = command(["parity", "--markdown"])
    render_text = command([
        "render", "04110", "--species", "human",
        "--gene-data", DATA / "hsa04110-shared-control-treatment.csv",
        "--kegg-dir", FIXTURES, "--out-dir", CLI_RESULTS,
        "--out-suffix", "cli-native", "--render-mode", "native",
        "--offline", "--quiet", "--no-key", "--limit", "2",
    ])
    sbgn_text = command([
        "sbgn", FIXTURES / "P00001.new.layout.sbgn",
        "--gene-data", DATA / "P00001-shared-control-treatment.csv",
        "--gene-idtype", "SYMBOL", "--out-dir", CLI_RESULTS,
        "--offline", "--quiet",
    ])
    smoke = subprocess.run(
        [sys.executable, "-m", "pathview.test_all_features"], cwd=WORKSPACE_ROOT,
        env=environment, text=True, capture_output=True, timeout=90,
    )
    require(smoke.returncode == 0, f"Bundled smoke test failed: {smoke.stdout}\n{smoke.stderr}")
    require("11 passed, 0 failed" in smoke.stdout, "Unexpected bundled smoke-test totals")

    (CLI_RESULTS / "version.txt").write_text(version + "\n")
    (CLI_RESULTS / "species-human.txt").write_text(species + "\n")
    (CLI_RESULTS / "parity.md").write_text(parity + "\n")
    (CLI_RESULTS / "render-stdout.txt").write_text(render_text + "\n")
    (CLI_RESULTS / "sbgn-stdout.txt").write_text(sbgn_text + "\n")
    (CLI_RESULTS / "smoke-test.txt").write_text(smoke.stdout + smoke.stderr)
    for path in sorted(CLI_RESULTS.iterdir()):
        if path.is_file():
            remember_output(path, "CLI or bundled smoke-test evidence")
    return {"version": version, "species": species.splitlines()[0],
            "parity_rows": parity.count("\n") - 1,
            "smoke_test": "11 passed, 0 failed"}


@check("project feature matrix is internally complete and testable")
def _parity_matrix():
    summary = pv.parity_summary()
    table = pv.feature_table()
    require(summary["total_features"] == table.height == 74, "Feature matrix row count changed")
    require(summary["full"] == 73 and summary["none"] == 0,
            "Project-declared feature statuses changed")
    table.write_csv(TABLES / "project-declared-feature-matrix.csv")
    remember_output(TABLES / "project-declared-feature-matrix.csv",
                    "Pathview Plus project-declared feature matrix")
    return {
        "summary": summary,
        "important_label": "These percentages are the repository's own declared matrix, not an independent scientific equivalence score.",
    }


def probe_null_csv_row():
    """Keep a beginner-facing input-cleaning observation without stopping the run."""
    data = pl.DataFrame(
        {"entrez": [1029, 1956, None],
         "Control": [-2.0, -1.2, None], "Treatment": [2.0, 1.2, None]},
        schema={"entrez": pl.Int64, "Control": pl.Float64, "Treatment": pl.Float64},
    )
    try:
        pv.pathview(
            "04110", gene_data=data, species="hsa", kegg_dir=FIXTURES,
            out_dir=FIGURES, out_suffix="null-row-probe", render_mode="native",
            map_symbol=False, plot_col_key=False, quiet=True,
        )
    except Exception as exc:
        REPORT["observations"].append({
            "id": "PY-OBS-001",
            "status": "needs review",
            "title": "A completely blank input row is not dropped automatically",
            "reproduction": "A three-row Polars DataFrame with one mapped ID, one unmatched ID, and one all-null row",
            "observed": f"{type(exc).__name__}: {exc}",
            "beginner_workaround": "Drop completely blank rows before calling pathview(), for example df.drop_nulls().",
            "scope": "Numeric Entrez IDs without a null row work; the null row is the trigger.",
        })
    else:
        REPORT["observations"].append({
            "id": "PY-OBS-001", "status": "not reproduced",
            "title": "Blank input row probe", "observed": "The call completed.",
        })


def write_reports():
    probe_null_csv_row()
    passed = sum(item["status"] == "pass" for item in REPORT["checks"])
    failed = sum(item["status"] == "fail" for item in REPORT["checks"])
    REPORT["summary"] = {"passed": passed, "failed": failed,
                         "total": len(REPORT["checks"])}
    REPORT["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    json_path = RESULTS / "comparison.json"
    json_path.write_text(json.dumps(REPORT, indent=2, default=str) + "\n")

    checks_path = RESULTS / "check-results.csv"
    with checks_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "name", "status", "seconds", "error"])
        writer.writeheader()
        for item in REPORT["checks"]:
            writer.writerow({key: item.get(key, "") for key in writer.fieldnames})

    manifest_path = RESULTS / "output-manifest.csv"
    fields = ["path", "purpose", "exists", "bytes", "sha256", "width_px", "height_px", "mode"]
    with manifest_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in REPORT["outputs"]:
            writer.writerow({key: item.get(key, "") for key in fields})

    print(f"\n{passed} passed, {failed} failed")
    print(f"Evidence: {relative(json_path)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(write_reports())
