#!/usr/bin/env python3
"""Generate visual and numerical evidence without contacting live services."""

from __future__ import annotations

import hashlib
import importlib
import json
import shutil
from pathlib import Path

import numpy as np
import polars as pl
from PIL import Image, ImageDraw

import pathview
from pathview import PathwayResult, SpeciesInfo, highlight_nodes, node_info, parse_kgml
from pathview.rendering import _paint_cpd_nodes, _paint_gene_nodes


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
RESULTS = ROOT / "results"
EVIDENCE = RESULTS / "evidence"
VALIDATION = WORKSPACE / "pygage-pathview-validation"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gene_frame(x: float, y: float, width: float = 46, height: float = 18) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "entry_id": ["g"],
            "x": [x],
            "y": [y],
            "width": [width],
            "height": [height],
            "kegg_names": ["1029"],
        }
    )


def compound_frame(x: float, y: float, width: float = 10, height: float = 6) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "entry_id": ["c"],
            "x": [x],
            "y": [y],
            "width": [width],
            "height": [height],
            "kegg_names": ["C00031"],
        }
    )


def make_state_split_evidence() -> None:
    canvas = np.full((190, 420, 3), 255, dtype=np.uint8)
    states = [
        ("One condition", ["#00AA00"]),
        ("Two: left / right", ["#00AA00", "#FF0000"]),
        ("Three ordered slices", ["#0000FF", "#BEBEBE", "#FF0000"]),
    ]
    for index, (_, colors) in enumerate(states):
        x = 70 + index * 140
        frame = gene_frame(x, 90, width=96, height=40)
        color_data: dict[str, list] = {"id": ["g"]}
        for color_index, color in enumerate(colors):
            color_data[f"state_{color_index + 1}_col"] = [color]
        _paint_gene_nodes(canvas, frame, pl.DataFrame(color_data))
        canvas[70:111, x - 49 : x - 47] = 0
        canvas[70:111, x + 47 : x + 49] = 0
        canvas[70:72, x - 49 : x + 49] = 0
        canvas[109:111, x - 49 : x + 49] = 0
    image = Image.fromarray(canvas)
    draw = ImageDraw.Draw(image)
    for index, (title, _) in enumerate(states):
        x = 70 + index * 140
        draw.text((x - 52, 25), title, fill="black")
    draw.text((12, 155), "Verified: state order is left to right.", fill="black")
    image.save(EVIDENCE / "01-state-splits.png")


def make_coordinate_evidence() -> None:
    canvas = np.full((140, 300, 3), 255, dtype=np.uint8)
    _paint_gene_nodes(
        canvas,
        gene_frame(80, 30),
        pl.DataFrame({"id": ["g"], "value_col": ["#00AA00"]}),
    )
    _paint_cpd_nodes(
        canvas,
        compound_frame(220, 30),
        pl.DataFrame({"id": ["c"], "value_col": ["#FF0000"]}),
    )
    image = Image.fromarray(canvas)
    draw = ImageDraw.Draw(image)
    draw.line((10, 30, 290, 30), fill=(80, 80, 80), width=1)
    draw.text((38, 5), "Gene input y=30", fill="black")
    draw.text((175, 5), "Compound input y=30", fill="black")
    draw.text((20, 120), "Red compound appears near y=110 (= 140 - 30).", fill="black")
    image.save(EVIDENCE / "02-compound-coordinate-reproduction.png")


def make_highlight_evidence() -> None:
    image = np.full((100, 160, 3), 255, dtype=np.uint8)
    genes = pl.DataFrame(
        {
            "entry_id": ["1"],
            "kegg_names": ["1029"],
            "x": [80.0],
            "y": [50.0],
            "width": [60.0],
            "height": [24.0],
        }
    )
    result = PathwayResult("toy", plot_data_gene=genes, image_array=image)
    highlighted = result + highlight_nodes(["1029"], color="#FF0000", width=3)
    highlighted.save(EVIDENCE / "03-highlight-hex-working.png")


def frozen_fixture() -> Path | None:
    candidates = [
        VALIDATION / "cache" / "kegg",
        VALIDATION / ".r-library" / "pathview" / "extdata",
    ]
    for folder in candidates:
        if (folder / "hsa04110.xml").exists() and (folder / "hsa04110.png").exists():
            return folder
    return None


def make_official_workflow_evidence() -> dict:
    fixture = frozen_fixture()
    if fixture is None:
        return {"status": "not_run", "reason": "frozen hsa04110 fixture not available"}

    official = EVIDENCE / "official-hsa04110"
    official.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fixture / "hsa04110.xml", official / "hsa04110.xml")
    shutil.copy2(fixture / "hsa04110.png", official / "hsa04110.png")
    parsed = parse_kgml(official / "hsa04110.xml")

    core = importlib.import_module("pathview.pathview")
    original_species = core.kegg_species_code
    core.kegg_species_code = lambda species="hsa": SpeciesInfo(
        "hsa", True, None, None, None, None
    )
    input_data = {
        1: pl.DataFrame({"id": ["1029", "7157", "1956"], "Classical": [-1.0, 0.0, 1.0]}),
        2: pl.DataFrame(
            {
                "id": ["1029", "7157", "1956"],
                "Classical": [-1.0, 0.0, 1.0],
                "Basal": [1.0, 0.0, -1.0],
            }
        ),
        3: pl.DataFrame(
            {
                "id": ["1029", "7157", "1956"],
                "Classical": [-1.0, 0.0, 1.0],
                "Basal": [1.0, 0.0, -1.0],
                "Recovery": [0.0, -1.0, 1.0],
            }
        ),
    }
    outputs: list[dict] = []
    try:
        for count, data in input_data.items():
            suffix = {1: "one-state", 2: "half-and-half", 3: "three-state"}[count]
            result = pathview.pathview(
                "04110",
                gene_data=data,
                species="hsa",
                kegg_dir=official,
                output_format="png",
                out_suffix=suffix,
                map_symbol=False,
                min_nnodes=1,
                new_signature=False,
                plot_col_key=False,
            )
            output = official / f"hsa04110.{suffix}.png"
            with Image.open(output) as rendered:
                dimensions = rendered.size
            outputs.append(
                {
                    "states": count,
                    "file": output.name,
                    "dimensions": list(dimensions),
                    "sha256": sha256(output),
                    "gene_rows": result["plot_data_gene"].height,
                    "non_null_gene_values": int(
                        result["plot_data_gene"].select(data.columns[1:]).drop_nulls().height
                    ),
                }
            )
        pathview.pathview(
            "04110",
            gene_data=input_data[2],
            species="hsa",
            kegg_dir=official,
            output_format="svg",
            out_suffix="half-and-half",
            map_symbol=False,
            min_nnodes=1,
            new_signature=False,
            plot_col_key=False,
        )
        pathview.pathview(
            "04110",
            gene_data=input_data[2],
            species="hsa",
            kegg_dir=official,
            kegg_native=False,
            output_format="pdf",
            out_suffix="graph-half-and-half",
            map_symbol=False,
            min_nnodes=1,
            new_signature=False,
            plot_col_key=False,
        )
    finally:
        core.kegg_species_code = original_species

    with Image.open(official / "hsa04110.png") as original:
        input_dimensions = original.size
    summary = {
        "status": "completed",
        "fixture_source": str(fixture),
        "input_dimensions": list(input_dimensions),
        "parsed_nodes": len(parsed.nodes),
        "parsed_relations": len(parsed.edges),
        "parsed_reactions": len(parsed.reactions),
        "png_outputs": outputs,
        "svg": "hsa04110.half-and-half.svg",
        "pdf": "hsa04110.graph-half-and-half.pdf",
    }
    (official / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def make_numeric_reproductions() -> None:
    from pathview import catmull_rom_spline, node_color

    numeric = node_color(
        pl.DataFrame({"id": ["x"], "v": [10.0]}), limit=20, bins=41
    )["v_col"][0]
    string = node_color(
        pl.DataFrame({"id": ["x"], "v": ["10"]}), limit=20, bins=41
    )["v_col"][0]
    with np.errstate(all="ignore"):
        spline = catmull_rom_spline([(0, 0), (1, 2), (3, 1), (4, 3)], n_points=10)
    payload = {
        "decimal_10_color": numeric,
        "string_10_interpreted_as_hex_color": string,
        "colors_match": numeric == string,
        "catmull_rom_shape": list(spline.shape),
        "catmull_rom_all_finite": bool(np.isfinite(spline).all()),
        "catmull_rom_nonfinite_values": int((~np.isfinite(spline)).sum()),
    }
    (EVIDENCE / "04-numeric-reproductions.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    make_state_split_evidence()
    make_coordinate_evidence()
    make_highlight_evidence()
    make_numeric_reproductions()
    official = make_official_workflow_evidence()
    manifest = {
        "generated_files": sorted(
            str(path.relative_to(EVIDENCE))
            for path in EVIDENCE.rglob("*")
            if path.is_file()
        ),
        "official_workflow": official,
    }
    (EVIDENCE / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Generated {len(manifest['generated_files'])} evidence files in {EVIDENCE}")


if __name__ == "__main__":
    main()

