#!/usr/bin/env python3
"""Execute Pathview Plus workflows, including exact multi-state image checks."""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import shutil
import time
import traceback
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import polars as pl
from PIL import Image

import pathview
from pathview import SpeciesInfo, download_kegg, node_color, node_info, node_map, parse_kgml
from pathview.rendering import _paint_gene_nodes


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "results" / "pathview_python"
CACHE = ROOT / "cache" / "kegg"
R_EXTDATA = ROOT / ".r-library" / "pathview" / "extdata"
OUT.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)

REPORT: dict[str, object] = {
    "component": "Pathview Plus",
    "repository_commit": "07aee813375347bcc933ad21b4aed561dd7cd3bf",
    "distribution_version": "2.0.2",
    "runtime_version": pathview.__version__,
    "python": platform.python_version(),
    "checks": [],
}


def check(name: str, fn) -> object | None:
    started = time.perf_counter()
    try:
        details = fn()
        REPORT["checks"].append({
            "name": name,
            "status": "pass",
            "seconds": round(time.perf_counter() - started, 4),
            "details": details,
        })
        print(f"PASS  {name}")
        return details
    except Exception as exc:
        REPORT["checks"].append({
            "name": name,
            "status": "fail",
            "seconds": round(time.perf_counter() - started, 4),
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        })
        print(f"FAIL  {name}: {exc}")
        return None


def not_run(name: str, reason: str) -> None:
    REPORT["checks"].append({"name": name, "status": "not_run", "reason": reason})
    print(f"NOT RUN  {name}: {reason}")


def frozen_fixture() -> dict[str, object]:
    for suffix in ("xml", "png"):
        src = R_EXTDATA / f"hsa04110.{suffix}"
        if not src.exists():
            raise FileNotFoundError(f"R pathview fixture not installed: {src}")
        shutil.copy2(src, CACHE / src.name)
    parsed = parse_kgml(CACHE / "hsa04110.xml")
    frame = node_info(parsed)
    return {
        "source": "Bioconductor pathview 1.52.0 extdata",
        "nodes": frame.height,
        "gene_nodes": frame.filter(pl.col("type") == "gene").height,
        "png_size": list(Image.open(CACHE / "hsa04110.png").size),
    }


def live_species_lookup() -> dict[str, object]:
    from pathview import kegg_species_code

    info = kegg_species_code("hsa")
    if info.kegg_code != "hsa":
        raise AssertionError(info)
    return {"kegg_code": info.kegg_code}


def patch_human_species_lookup() -> None:
    """Isolate rendering from the currently failing organism-list service call."""
    module = importlib.import_module("pathview.pathview")
    original = module.kegg_species_code

    def resolver(species: str = "hsa") -> SpeciesInfo:
        if species in {"hsa", "human", "Homo sapiens"}:
            return SpeciesInfo("hsa", True, None, None, None, None)
        return original(species)

    module.kegg_species_code = resolver


PALETTE = {
    "limit": {"gene": 2.0, "cpd": 2.0},
    "bins": {"gene": 11, "cpd": 11},
    "both_dirs": {"gene": True, "cpd": True},
    "low": {"gene": "#00FF00", "cpd": "#0000FF"},
    "mid": {"gene": "#BEBEBE", "cpd": "#BEBEBE"},
    "high": {"gene": "#FF0000", "cpd": "#FFFF00"},
}


def mapped_count(frame: pl.DataFrame | None, state_columns: list[str]) -> dict[str, int]:
    if frame is None:
        return {name: 0 for name in state_columns}
    return {name: frame.filter(pl.col(name).is_not_null()).height for name in state_columns}


def run_python_pathview(
    pathway_id: str,
    gene_file: Path | None,
    compound_file: Path | None,
    species: str,
    suffix: str,
    output_format: str = "png",
    kegg_native: bool = True,
) -> dict[str, object]:
    gene = pl.read_csv(gene_file, schema_overrides={"gene_id": pl.String}) if gene_file else None
    compound = pl.read_csv(compound_file, schema_overrides={"compound_id": pl.String}) if compound_file else None
    result = pathview.pathview(
        pathway_id,
        gene_data=gene,
        cpd_data=compound,
        species=species,
        kegg_dir=CACHE,
        kegg_native=kegg_native,
        output_format=output_format,
        gene_idtype="ENTREZ" if species != "ko" else "KEGG",
        cpd_idtype="KEGG",
        out_suffix=suffix,
        map_symbol=False,
        new_signature=False,
        plot_col_key=False,
        **PALETTE,
    )
    if not result:
        raise AssertionError("pathview returned an empty result")
    gene_states = gene.columns[1:] if gene is not None else []
    compound_states = compound.columns[1:] if compound is not None else []
    prefix = pathway_id if pathway_id.startswith(species) else f"{species}{pathway_id}"
    extension = "png" if kegg_native and output_format == "png" else ("svg" if output_format == "svg" else "pdf")
    output = CACHE / f"{prefix}.{suffix}.{extension}"
    if not output.exists() or output.stat().st_size == 0:
        raise AssertionError(f"missing output {output}")
    destination = OUT / output.name
    shutil.copy2(output, destination)
    gene_frame = result.get("plot_data_gene")
    cpd_frame = result.get("plot_data_cpd")
    if gene_frame is not None:
        gene_frame.write_csv(OUT / f"{prefix}.{suffix}.gene_nodes.csv")
    if cpd_frame is not None:
        cpd_frame.write_csv(OUT / f"{prefix}.{suffix}.compound_nodes.csv")
    if extension == "png":
        with Image.open(output) as image:
            file_details = {"format": image.format, "size": list(image.size)}
    elif extension == "svg":
        file_details = {"root": ET.parse(output).getroot().tag, "bytes": output.stat().st_size}
    else:
        file_details = {"header": output.read_bytes()[:5].decode("ascii"), "bytes": output.stat().st_size}
    return {
        "output": str(destination.relative_to(ROOT)),
        "file": file_details,
        "gene_mapped_by_state": mapped_count(gene_frame, gene_states),
        "compound_mapped_by_state": mapped_count(cpd_frame, compound_states),
        "gene_node_rows": gene_frame.height if gene_frame is not None else 0,
        "compound_node_rows": cpd_frame.height if cpd_frame is not None else 0,
    }


def exact_half_and_half_image_test() -> dict[str, object]:
    pathway = parse_kgml(CACHE / "hsa04110.xml")
    nodes = node_info(pathway)
    genes = pl.read_csv(DATA / "half_and_half_hsa04110.csv", schema_overrides={"gene_id": pl.String})
    plot = node_map(genes, nodes, node_types="gene")
    if plot is None:
        raise AssertionError("gene mapping returned no table")
    colors = node_color(
        plot.select("entry_id", "Classical", "Basal").rename({"entry_id": "id"}),
        limit=2.0,
        bins=11,
        low="#00FF00",
        mid="#BEBEBE",
        high="#FF0000",
    )
    image = np.array(Image.open(CACHE / "hsa04110.png").convert("RGB"))
    painted = _paint_gene_nodes(image.copy(), plot, colors)
    raw_output = OUT / "hsa04110.half_half.raw_overlay.png"
    Image.fromarray(painted).save(raw_output)

    targets = plot.filter(pl.col("name").str.contains("hsa:1029") & pl.col("Classical").is_not_null())
    if targets.is_empty():
        raise AssertionError("CDKN2A / Entrez 1029 did not map")
    row = targets.row(0, named=True)
    x, y = int(row["x"]), int(row["y"])
    half_width, half_height = int(row["width"] / 2), int(row["height"] / 2)
    crop = painted[y - half_height:y + half_height, x - half_width:x + half_width]
    middle = crop.shape[1] // 2
    left, right = crop[:, :middle], crop[:, middle:]

    def count(region: np.ndarray, rgb: tuple[int, int, int]) -> int:
        return int(np.all(region == np.array(rgb), axis=2).sum())

    counts = {
        "left_green": count(left, (0, 255, 0)),
        "right_green": count(right, (0, 255, 0)),
        "left_red": count(left, (255, 0, 0)),
        "right_red": count(right, (255, 0, 0)),
    }
    if not (counts["left_green"] > counts["right_green"] and counts["right_red"] > counts["left_red"]):
        raise AssertionError(f"half-and-half directional colors failed: {counts}")
    return {
        "gene": "1029 (CDKN2A)",
        "first_column": "Classical = -2.0 = left green half",
        "second_column": "Basal = +2.0 = right red half",
        "pixel_counts": counts,
        "output": str(raw_output.relative_to(ROOT)),
    }


def direct_download(pathway_id: str, species: str) -> dict[str, object]:
    status = download_kegg(pathway_id, species=species, kegg_dir=CACHE, file_type=["xml", "png"])
    full = pathway_id if pathway_id.startswith(species) else f"{species}{pathway_id}"
    if status.get(full) != "succeed":
        raise RuntimeError(status)
    xml = CACHE / f"{full}.xml"
    png = CACHE / f"{full}.png"
    parsed = parse_kgml(xml)
    with Image.open(png) as image:
        size = list(image.size)
    return {"pathway": full, "nodes": len(parsed.nodes), "png_size": size}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--live",
        action="store_true",
        help="also query current KEGG services and run the pathways that need fresh downloads",
    )
    args = parser.parse_args(argv)

    check("frozen official hsa04110 fixture", frozen_fixture)
    patch_human_species_lookup()

    check(
        "classical one-condition Cell Cycle PNG",
        lambda: run_python_pathview("04110", DATA / "classical_hsa04110.csv", None, "hsa", "classical"),
    )
    check(
        "two-condition left/right half PNG",
        lambda: run_python_pathview("04110", DATA / "half_and_half_hsa04110.csv", None, "hsa", "half_half"),
    )
    check("exact half-and-half pixels on CDKN2A", exact_half_and_half_image_test)
    check(
        "three-condition Cell Cycle PNG",
        lambda: run_python_pathview("04110", DATA / "three_state_hsa04110.csv", None, "hsa", "three_state"),
    )
    check(
        "two-condition SVG vector output",
        lambda: run_python_pathview(
            "04110", DATA / "half_and_half_hsa04110.csv", None, "hsa", "half_half", output_format="svg"
        ),
    )

    if args.live:
        check("live KEGG species resolution used by normal hsa calls", live_species_lookup)
        for pathway_id, species in [("04151", "hsa"), ("04010", "hsa"), ("00010", "hsa"), ("00910", "ko")]:
            check(f"direct KEGG KGML/PNG download {species}{pathway_id}", lambda p=pathway_id, s=species: direct_download(p, s))
        check(
            "classical one-condition PI3K-Akt PNG",
            lambda: run_python_pathview("04151", DATA / "classical_hsa04151.csv", None, "hsa", "pi3k_classical"),
        )
        check(
            "three-condition MAPK PNG",
            lambda: run_python_pathview("04010", DATA / "three_state_hsa04010.csv", None, "hsa", "mapk_three_state"),
        )
        check(
            "gene plus compound glycolysis PNG",
            lambda: run_python_pathview(
                "00010",
                DATA / "gene_and_compound_hsa00010_genes.csv",
                DATA / "gene_and_compound_hsa00010_compounds.csv",
                "hsa",
                "gene_compound",
            ),
        )
        check(
            "KEGG Orthology nitrogen-metabolism PNG",
            lambda: run_python_pathview("00910", DATA / "ko00910.csv", None, "ko", "ko_function"),
        )
    else:
        reason = "requires live KEGG access; rerun scripts/run_pathview_validation.py --live"
        for name in (
            "live KEGG species resolution",
            "fresh PI3K-Akt pathway",
            "fresh MAPK pathway",
            "fresh glycolysis gene+compound pathway",
            "fresh KO nitrogen-metabolism pathway",
        ):
            not_run(name, reason)
    check(
        "graph-layout PDF output",
        lambda: run_python_pathview(
            "04110",
            DATA / "half_and_half_hsa04110.csv",
            None,
            "hsa",
            "graph",
            output_format="pdf",
            kegg_native=False,
        ),
    )

    output = OUT / "validation.json"
    output.write_text(json.dumps(REPORT, indent=2, default=str))
    failures = sum(c["status"] == "fail" for c in REPORT["checks"])
    not_run_count = sum(c["status"] == "not_run" for c in REPORT["checks"])
    print(f"\nWrote {output}")
    print(
        f"Pathview Plus checks: {len(REPORT['checks']) - failures - not_run_count} passed, "
        f"{failures} failed, {not_run_count} not run"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
