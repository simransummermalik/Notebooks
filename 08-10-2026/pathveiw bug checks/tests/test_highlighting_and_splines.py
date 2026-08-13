from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl
import pytest
from PIL import Image

from pathview import (
    PathwayResult,
    bezier_to_svg_path,
    catmull_rom_spline,
    change_labels,
    cubic_bezier,
    highlight_edges,
    highlight_nodes,
    highlight_path,
    quadratic_bezier,
    route_edge_spline,
    smooth_path_svg,
)
from pathview.highlighting import _draw_border, _draw_line


def _centered_genes() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "entry_id": ["1", "2"],
            "kegg_names": ["1029", "7157"],
            "x": [30.0, 70.0],
            "y": [50.0, 50.0],
            "width": [20.0, 20.0],
            "height": [10.0, 10.0],
        }
    )


@pytest.mark.highlighting
def test_hex_node_highlight_returns_copy_and_preserves_original() -> None:
    original_image = np.full((100, 100, 3), 255, dtype=np.uint8)
    original = PathwayResult(
        "hsa00001", plot_data_gene=_centered_genes(), image_array=original_image
    )
    modified = original + highlight_nodes(["1029"], color="#FF0000", width=2)
    assert modified is not original
    assert modified.modifications and not original.modifications
    assert np.array_equal(original.image_array, original_image)
    assert not np.array_equal(modified.image_array, original.image_array)


@pytest.mark.highlighting
def test_missing_highlight_identifier_is_a_no_op() -> None:
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    result = PathwayResult("hsa00001", plot_data_gene=_centered_genes(), image_array=image)
    modified = result + highlight_nodes(["not-present"], color="#FF0000")
    assert np.array_equal(modified.image_array, image)


@pytest.mark.highlighting
def test_hex_edge_and_path_highlights_modify_image() -> None:
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    result = PathwayResult("hsa00001", plot_data_gene=_centered_genes(), image_array=image)
    edge = result + highlight_edges([("1029", "7157")], color="#0000FF", width=1)
    full_path = result + highlight_path(
        ["1029", "7157"], color="#FF8800", node_width=2, edge_width=1
    )
    assert not np.array_equal(edge.image_array, image)
    assert not np.array_equal(full_path.image_array, image)


@pytest.mark.highlighting
def test_modified_result_saves_png_and_pdf(tmp_path: Path) -> None:
    image = np.full((40, 60, 3), 255, dtype=np.uint8)
    result = PathwayResult("toy", image_array=image)
    png = tmp_path / "saved.png"
    pdf = tmp_path / "saved.pdf"
    result.save(png)
    result.save(pdf, format="pdf")
    assert png.read_bytes().startswith(b"\x89PNG")
    assert pdf.read_bytes().startswith(b"%PDF")


@pytest.mark.highlighting
def test_save_without_image_has_clear_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No image data"):
        PathwayResult("toy").save(tmp_path / "none.png")


@pytest.mark.highlighting
@pytest.mark.xfail(
    reason="PV-BUG-032: documented/default named highlight colors are parsed as six-digit hex"
)
def test_default_named_node_highlight_color_works() -> None:
    result = PathwayResult(
        "toy",
        plot_data_gene=_centered_genes(),
        image_array=np.full((100, 100, 3), 255, dtype=np.uint8),
    )
    modified = result + highlight_nodes(["1029"])
    assert not np.array_equal(modified.image_array, result.image_array)


@pytest.mark.highlighting
@pytest.mark.xfail(
    reason="PV-BUG-039: highlights flip y but native gene painting does not, so borders miss noncentral nodes"
)
def test_highlight_border_uses_same_coordinates_as_native_gene_node() -> None:
    genes = pl.DataFrame(
        {
            "entry_id": ["1"],
            "kegg_names": ["1029"],
            "x": [30.0],
            "y": [20.0],
            "width": [20.0],
            "height": [10.0],
        }
    )
    result = PathwayResult(
        "toy", plot_data_gene=genes, image_array=np.full((100, 100, 3), 255, dtype=np.uint8)
    )
    modified = result + highlight_nodes(["1029"], color="#FF0000", width=1)
    assert np.array_equal(modified.image_array[15, 30], [255, 0, 0])
    assert np.array_equal(modified.image_array[80, 30], [255, 255, 255])


@pytest.mark.highlighting
@pytest.mark.xfail(reason="PV-BUG-040: highlight opacity argument is ignored")
def test_border_opacity_blends_with_existing_pixels() -> None:
    image = np.full((40, 40, 3), 255, dtype=np.uint8)
    _draw_border(
        image,
        cx=20,
        cy=20,
        half_width=5,
        half_height=5,
        img_height=40,
        rgb=(255, 0, 0),
        thickness=1,
        opacity=0.5,
    )
    assert np.array_equal(image[15, 20], [255, 128, 128])


@pytest.mark.highlighting
@pytest.mark.xfail(reason="PV-BUG-041: change_labels records metadata but does not alter the saved image")
def test_change_labels_visibly_changes_rendered_result() -> None:
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    result = PathwayResult("toy", plot_data_gene=_centered_genes(), image_array=image)
    changed = result + change_labels({"1029": "CDKN2A*"}, font_size=12, color="#000000")
    assert not np.array_equal(changed.image_array, image)


@pytest.mark.highlighting
@pytest.mark.xfail(reason="PV-BUG-042: edge highlighting builds positions from genes only")
def test_edge_highlighting_supports_compounds() -> None:
    genes = _centered_genes().head(1)
    compounds = pl.DataFrame(
        {
            "entry_id": ["3"],
            "kegg_names": ["C00031"],
            "x": [70.0],
            "y": [50.0],
            "width": [10.0],
            "height": [10.0],
        }
    )
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    result = PathwayResult(
        "toy",
        plot_data_gene=genes,
        plot_data_cpd=compounds,
        image_array=image,
    )
    changed = result + highlight_edges([("1029", "C00031")], color="#0000FF", width=1)
    assert not np.array_equal(changed.image_array, image)


@pytest.mark.highlighting
@pytest.mark.xfail(reason="PV-BUG-043: requested one-pixel line is drawn two pixels thick")
def test_line_thickness_one_is_exactly_one_pixel() -> None:
    image = np.full((30, 30, 3), 255, dtype=np.uint8)
    _draw_line(
        image,
        x1=5,
        y1=15,
        x2=20,
        y2=15,
        img_height=30,
        rgb=(0, 0, 255),
        thickness=1,
    )
    colored_rows = np.where(np.any(np.any(image != 255, axis=2), axis=1))[0]
    assert colored_rows.tolist() == [15]


@pytest.mark.highlighting
@pytest.mark.xfail(
    reason="PV-BUG-044: save() does not infer PDF from path and writes PNG bytes to a .pdf name"
)
def test_save_infers_format_from_file_extension(tmp_path: Path) -> None:
    output = tmp_path / "inferred.pdf"
    PathwayResult("toy", image_array=np.zeros((10, 10, 3), dtype=np.uint8)).save(output)
    assert output.read_bytes().startswith(b"%PDF")


@pytest.mark.highlighting
@pytest.mark.xfail(reason="PV-BUG-072: highlight drawing cannot assign RGB tuples into RGBA arrays")
def test_highlighting_supports_rgba_pathway_images() -> None:
    image = np.full((100, 100, 4), 255, dtype=np.uint8)
    result = PathwayResult("toy", plot_data_gene=_centered_genes(), image_array=image)
    changed = result + highlight_nodes(["1029"], color="#FF0000", width=1)
    assert changed.image_array.shape == (100, 100, 4)
    assert np.all(changed.image_array[:, :, 3] == 255)


@pytest.mark.highlighting
@pytest.mark.xfail(
    reason="PV-BUG-073: dynamic label-change metadata is lost when another layer is chained"
)
def test_label_changes_survive_later_highlight_layers() -> None:
    image = np.full((100, 100, 3), 255, dtype=np.uint8)
    result = PathwayResult("toy", plot_data_gene=_centered_genes(), image_array=image)
    labeled = result + change_labels({"1029": "CDKN2A*"})
    chained = labeled + highlight_nodes(["1029"], color="#FF0000", width=1)
    assert chained._label_changes == {"1029": "CDKN2A*"}


@pytest.mark.spline
@pytest.mark.parametrize("n_points", [2, 10, 51])
def test_cubic_bezier_shape_and_endpoints(n_points: int) -> None:
    curve = cubic_bezier((0, 0), (1, 2), (3, 2), (4, 0), n_points=n_points)
    assert curve.shape == (n_points, 2)
    np.testing.assert_allclose(curve[0], [0, 0])
    np.testing.assert_allclose(curve[-1], [4, 0])
    assert np.isfinite(curve).all()


@pytest.mark.spline
@pytest.mark.parametrize("n_points", [2, 10, 51])
def test_quadratic_bezier_shape_and_endpoints(n_points: int) -> None:
    curve = quadratic_bezier((0, 0), (2, 3), (4, 0), n_points=n_points)
    assert curve.shape == (n_points, 2)
    np.testing.assert_allclose(curve[0], [0, 0])
    np.testing.assert_allclose(curve[-1], [4, 0])
    assert np.isfinite(curve).all()


@pytest.mark.spline
def test_empty_bezier_svg_path_is_empty() -> None:
    assert bezier_to_svg_path(np.empty((0, 2))) == ""


@pytest.mark.spline
def test_bezier_svg_path_contains_all_samples_and_optional_close() -> None:
    curve = np.array([[0.0, 0.0], [1.0, 2.0], [3.0, 4.0]])
    open_path = bezier_to_svg_path(curve)
    closed = bezier_to_svg_path(curve, close=True)
    assert open_path == "M 0.00 0.00 L 1.00 2.00 L 3.00 4.00"
    assert closed.endswith(" Z")


@pytest.mark.spline
@pytest.mark.parametrize(
    "points",
    [
        [(0, 0), (1, 2), (3, 1), (4, 3)],
        [(0, 0), (1, 1)],
        [(0, 0), (1, 1), (1, 1), (2, 0)],
    ],
)
@pytest.mark.xfail(
    reason="PV-BUG-045: duplicated phantom/repeated Catmull-Rom points cause zero denominators and NaNs"
)
def test_catmull_rom_documented_inputs_are_finite(points) -> None:
    curve = catmull_rom_spline(points, n_points=10)
    assert curve.shape[1] == 2
    assert np.isfinite(curve).all()
    np.testing.assert_allclose(curve[0], points[0])
    np.testing.assert_allclose(curve[-1], points[-1])


@pytest.mark.spline
def test_one_catmull_point_is_returned_unchanged() -> None:
    curve = catmull_rom_spline([(2, 3)])
    assert curve.shape == (1, 2)
    np.testing.assert_array_equal(curve, [[2, 3]])


@pytest.mark.spline
def test_straight_and_explicit_curved_routes() -> None:
    straight = route_edge_spline((0, 0), (10, 5), obstacles=[], routing_mode="straight")
    curved = route_edge_spline((0, 0), (10, 5), obstacles=[], routing_mode="curved")
    assert straight.shape == (2, 2)
    assert curved.shape == (30, 2)
    assert np.isfinite(curved).all()
    np.testing.assert_allclose(curved[[0, -1]], [[0, 0], [10, 5]])


@pytest.mark.spline
@pytest.mark.xfail(
    reason="PV-BUG-046: obstacles=None forces every routing mode to a straight two-point line"
)
def test_curved_routing_works_without_obstacle_list() -> None:
    curve = route_edge_spline((0, 0), (10, 5), routing_mode="curved")
    assert curve.shape == (30, 2)


@pytest.mark.spline
@pytest.mark.xfail(
    reason="PV-BUG-047: obstacles argument is not consulted by routing implementation"
)
def test_edge_route_avoids_supplied_obstacle() -> None:
    obstacle = (4.0, -1.0, 2.0, 2.0)
    curve = route_edge_spline(
        (0, 0), (10, 0), obstacles=[obstacle], routing_mode="curved"
    )
    x, y, width, height = obstacle
    inside = (
        (curve[:, 0] >= x)
        & (curve[:, 0] <= x + width)
        & (curve[:, 1] >= y)
        & (curve[:, 1] <= y + height)
    )
    assert not inside.any()


@pytest.mark.spline
@pytest.mark.xfail(
    reason="PV-BUG-048: orthogonal routing delegates to broken Catmull-Rom implementation"
)
def test_orthogonal_route_is_finite() -> None:
    curve = route_edge_spline((0, 0), (10, 5), obstacles=[], routing_mode="orthogonal")
    assert np.isfinite(curve).all()
    np.testing.assert_allclose(curve[[0, -1]], [[0, 0], [10, 5]])


@pytest.mark.spline
@pytest.mark.xfail(reason="PV-BUG-049: unknown routing mode silently falls back to straight")
def test_unknown_routing_mode_is_rejected() -> None:
    with pytest.raises(ValueError, match="routing_mode"):
        route_edge_spline((0, 0), (1, 1), obstacles=[], routing_mode="banana")


@pytest.mark.spline
@pytest.mark.xfail(reason="PV-BUG-050: smooth_path_svg tension parameter is unused")
def test_smooth_svg_tension_changes_curve() -> None:
    points = [(0, 0), (1, 2), (3, 1)]
    assert smooth_path_svg(points, tension=0.0) != smooth_path_svg(points, tension=1.0)


@pytest.mark.spline
@pytest.mark.xfail(reason="PV-BUG-051: nonfinite curve values are serialized directly into SVG")
def test_nonfinite_curve_is_rejected_before_svg_serialization() -> None:
    with pytest.raises(ValueError, match="finite|NaN"):
        bezier_to_svg_path(np.array([[0.0, 0.0], [np.nan, 1.0]]))
