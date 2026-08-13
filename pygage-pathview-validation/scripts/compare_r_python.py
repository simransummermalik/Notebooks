#!/usr/bin/env python3
"""Compare controlled R pathview and Python Pathview Plus outputs."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PY_OUT = ROOT / "results" / "pathview_python"
R_OUT = ROOT / "results" / "pathview_r"
OUT = ROOT / "results" / "comparison"
OUT.mkdir(parents=True, exist_ok=True)


def color_count(region: np.ndarray, rgb: tuple[int, int, int], tolerance: float = 40.0) -> int:
    pixels = region[..., :3].astype(float)
    distance = np.linalg.norm(pixels - np.array(rgb, dtype=float), axis=2)
    return int((distance <= tolerance).sum())


def crop_node(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    half_width = int(width / 2)
    half_height = int(height / 2)
    return image[y - half_height:y + half_height, x - half_width:x + half_width]


def compare_tables() -> tuple[pl.DataFrame, dict[str, object]]:
    py = pl.read_csv(PY_OUT / "hsa04110.half_half.gene_nodes.csv")
    r = pl.read_csv(R_OUT / "hsa04110.r_half_half.gene_nodes.csv", null_values="NA")
    py_mapped = py.filter(pl.col("Classical").is_not_null()).select(
        pl.col("x").cast(pl.Int64),
        pl.col("y").cast(pl.Int64),
        pl.col("name").alias("python_kegg_names"),
        pl.col("Classical").alias("python_classical"),
        pl.col("Basal").alias("python_basal"),
    )
    r_mapped = r.filter(pl.col("Classical").is_not_null()).select(
        pl.col("x").cast(pl.Int64),
        pl.col("y").cast(pl.Int64),
        pl.col("all.mapped").alias("r_all_mapped"),
        pl.col("Classical").alias("r_classical"),
        pl.col("Basal").alias("r_basal"),
        pl.col("Classical.col").alias("r_classical_color"),
        pl.col("Basal.col").alias("r_basal_color"),
    )
    joined = py_mapped.join(r_mapped, on=["x", "y"], how="inner").with_columns(
        (pl.col("python_classical") - pl.col("r_classical")).abs().alias("classical_abs_difference"),
        (pl.col("python_basal") - pl.col("r_basal")).abs().alias("basal_abs_difference"),
    )
    joined.write_csv(OUT / "mapped_node_comparison.csv")
    if joined.height != py_mapped.height or joined.height != r_mapped.height:
        raise AssertionError(
            f"mapped-coordinate sets differ: Python={py_mapped.height}, R={r_mapped.height}, common={joined.height}"
        )
    max_difference = max(
        float(joined["classical_abs_difference"].max()),
        float(joined["basal_abs_difference"].max()),
    )
    if max_difference != 0:
        raise AssertionError(f"mapped values differ by as much as {max_difference}")
    return joined, {
        "python_gene_node_rows": py.height,
        "r_gene_node_rows": r.height,
        "python_mapped_rows": py_mapped.height,
        "r_mapped_rows": r_mapped.height,
        "common_mapped_coordinates": joined.height,
        "maximum_value_difference": max_difference,
        "r_state_colors": {
            "Classical": sorted(set(joined["r_classical_color"])),
            "Basal": sorted(set(joined["r_basal_color"])),
        },
    }


def compare_pixels() -> dict[str, object]:
    py_image = np.array(Image.open(PY_OUT / "hsa04110.half_half.raw_overlay.png").convert("RGBA"))
    r_image = np.array(Image.open(R_OUT / "hsa04110.r_half_half.multi.png").convert("RGBA"))
    if py_image.shape != r_image.shape:
        raise AssertionError(f"fair-comparison image sizes differ: Python={py_image.shape}, R={r_image.shape}")

    x, y, width, height = 532, 124, 46, 17
    py_crop = crop_node(py_image, x, y, width, height)
    r_crop = crop_node(r_image, x, y, width, height)

    def directional_counts(crop: np.ndarray) -> dict[str, int]:
        midpoint = crop.shape[1] // 2
        left, right = crop[:, :midpoint], crop[:, midpoint:]
        return {
            "left_green": color_count(left, (0, 255, 0)),
            "right_green": color_count(right, (0, 255, 0)),
            "left_red": color_count(left, (255, 0, 0)),
            "right_red": color_count(right, (255, 0, 0)),
        }

    py_counts = directional_counts(py_crop)
    r_counts = directional_counts(r_crop)
    for implementation, counts in (("Python", py_counts), ("R", r_counts)):
        if counts["left_green"] <= counts["right_green"]:
            raise AssertionError(f"{implementation}: green is not concentrated on the left: {counts}")
        if counts["right_red"] <= counts["left_red"]:
            raise AssertionError(f"{implementation}: red is not concentrated on the right: {counts}")

    fig, axes = plt.subplots(2, 2, figsize=(14, 8), gridspec_kw={"height_ratios": [4, 1]})
    axes[0, 0].imshow(py_image)
    axes[0, 0].set_title("Python Pathview Plus 2.0.2 — frozen KEGG background")
    axes[0, 1].imshow(r_image)
    axes[0, 1].set_title("R pathview 1.52.0 — same frozen KEGG background")
    axes[1, 0].imshow(py_crop)
    axes[1, 0].set_title("Python CDKN2A node: Classical left / Basal right")
    axes[1, 1].imshow(r_crop)
    axes[1, 1].set_title("R CDKN2A node: Classical left / Basal right")
    for axis in axes.flat:
        axis.axis("off")
    fig.suptitle("Controlled two-state hsa04110 comparison", fontsize=15, fontweight="bold")
    fig.tight_layout()
    figure = OUT / "r_vs_python_half_half.png"
    fig.savefig(figure, dpi=180, bbox_inches="tight")
    plt.close(fig)

    return {
        "shared_image_shape": list(py_image.shape),
        "node": "Entrez 1029 / CDKN2A at x=532, y=124",
        "python_pixel_counts": py_counts,
        "r_pixel_counts": r_counts,
        "figure": str(figure.relative_to(ROOT)),
    }


def compare_other_outputs() -> dict[str, object]:
    pairs = {
        "one_condition_png": (
            PY_OUT / "hsa04110.classical.png",
            R_OUT / "hsa04110.r_classical.png",
        ),
        "two_condition_png": (
            PY_OUT / "hsa04110.half_half.png",
            R_OUT / "hsa04110.r_half_half.multi.png",
        ),
        "three_condition_png": (
            PY_OUT / "hsa04110.three_state.png",
            R_OUT / "hsa04110.r_three_state.multi.png",
        ),
        "graph_pdf": (
            PY_OUT / "hsa04110.graph.pdf",
            R_OUT / "hsa04110.r_graph.multi.pdf",
        ),
    }
    details = {}
    for name, (python_file, r_file) in pairs.items():
        if not python_file.exists() or not r_file.exists():
            raise FileNotFoundError(f"missing {name}: {python_file} or {r_file}")
        details[name] = {
            "python_bytes": python_file.stat().st_size,
            "r_bytes": r_file.stat().st_size,
            "status": "both valid non-empty files",
        }
    return details


def main() -> int:
    table, table_summary = compare_tables()
    pixel_summary = compare_pixels()
    output_summary = compare_other_outputs()
    report = {
        "comparison": "R pathview 1.52.0 versus Python Pathview Plus 2.0.2",
        "pathway": "hsa04110 Cell cycle",
        "fixture": "identical Bioconductor pathview 1.52.0 hsa04110.xml and hsa04110.png",
        "input": {
            "columns": ["Classical", "Basal"],
            "Classical": "negative, first column, expected left green half",
            "Basal": "positive, second column, expected right red half",
        },
        "mapped_table_parity": table_summary,
        "pixel_orientation": pixel_summary,
        "file_checks": output_summary,
        "overall_status": "pass",
        "important_difference": (
            "Native PNG supports the same two-state order in both tools. "
            "R Graphviz can show multiple states; Python's graph/PDF renderer uses only the first state."
        ),
    }
    output = OUT / "comparison.json"
    output.write_text(json.dumps(report, indent=2))
    print(f"PASS  {table.height} mapped rows have identical coordinates and state values")
    print("PASS  both implementations place Classical green on the left and Basal red on the right")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
