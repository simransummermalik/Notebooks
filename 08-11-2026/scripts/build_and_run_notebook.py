#!/usr/bin/env python3
"""Build and execute the beginner-readable August 11 comparison notebook."""

from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path
from textwrap import dedent

import nbformat as nbf
from nbclient import NotebookClient


DAY_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = DAY_ROOT / "notebooks"
EXECUTED = NOTEBOOKS / "executed"
NOTEBOOKS.mkdir(parents=True, exist_ok=True)
EXECUTED.mkdir(parents=True, exist_ok=True)


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


cells = [
    md(
        """
        # R vs Python Pathview — my comparison

        **Work date:** August 11, 2026  
        **Comparison question:** How does the new Python Pathview Plus
        compare with R Pathview and R SBGNview?

        I used the same pathway files and small input tables for all three
        programs. I put the observations first and left the checks below them
        so I could see where each number came from. The saved run completed
        without an error in any code cell.
        """
    ),
    md(
        """
        ## The comparison

        | Comparison | What matched | What was different |
        |---|---|---|
        | R Pathview vs Pathview Plus | All 5 shared genes, left/right condition order, 1039 x 801 raw map, and genes plus compounds | Python reported repeated/grouped KEGG rows, and C00022 was smaller |
        | R SBGNview vs Pathview Plus | All 7 shared genes, 78 total glyphs, 83 arcs, and left/right condition order | R added 3 VAT1 matches from SLC18A2; Python did not draw state/clone marks |

        The main examples ran in both programs. I still found a few details
        that need another look, especially compound size and SBGN labels.
        """
    ),
    code(
        """
        from pathlib import Path
        import hashlib
        import json
        import os
        import subprocess

        import matplotlib.pyplot as plt
        import polars as pl
        from PIL import Image
        from IPython.display import display, Image as NotebookImage
        import pathview as pv

        DAY_ROOT = Path.cwd()
        if DAY_ROOT.name == "notebooks":
            DAY_ROOT = DAY_ROOT.parent
        assert (DAY_ROOT / "results").exists(), "Run this notebook from the 08-11-2026 folder."

        FIXTURES = DAY_ROOT / "sources" / "pathview-plus" / "tests" / "fixtures"
        DATA = DAY_ROOT / "data"
        RESULTS = DAY_ROOT / "results"
        NOTEBOOK_RESULTS = RESULTS / "notebook"
        NOTEBOOK_RESULTS.mkdir(parents=True, exist_ok=True)

        os.environ["MPLBACKEND"] = "Agg"
        os.environ["PATHVIEW_CACHE"] = str(DAY_ROOT / "cache" / "pathview-plus")
        pv.set_offline(True)

        def sha256(path):
            return hashlib.sha256(Path(path).read_bytes()).hexdigest()

        def show_pair(left, right, left_title, right_title):
            fig, axes = plt.subplots(1, 2, figsize=(16, 6))
            for axis, path, title in zip(axes, [left, right], [left_title, right_title]):
                axis.imshow(plt.imread(path))
                axis.set_title(title)
                axis.axis("off")
            plt.tight_layout()
            plt.show()

        print("Notebook setup complete.")
        print("Pathview Plus version:", pv.__version__)
        """
    ),
    md(
        """
        ## Version I tested

        I tested Pathview Plus 3.1.0 at commit
        [`d4d45de`](https://github.com/raw-lab/pathview-plus/commit/d4d45decec56e1ebec15cf04ae62ff944851780e),
        along with R Pathview 1.52.0 and R SBGNview 1.26.0.
        """
    ),
    code(
        """
        python_report = json.loads((RESULTS / "python-pathview" / "comparison.json").read_text())
        r_pathview_report = json.loads((RESULTS / "r-pathview" / "comparison.json").read_text())
        r_sbgn_report = json.loads((RESULTS / "sbgnview" / "r-comparison.json").read_text())
        python_sbgn_report = json.loads((RESULTS / "sbgnview" / "python-comparison.json").read_text())
        v3_audit = json.loads((RESULTS / "v3-audit" / "old-findings-status.json").read_text())

        commit = subprocess.check_output(
            ["git", "-C", str(DAY_ROOT / "sources" / "pathview-plus"), "rev-parse", "HEAD"],
            text=True,
        ).strip()

        versions = pl.DataFrame([
            {"part": "Pathview Plus", "version": pv.__version__},
            {"part": "Pathview Plus commit", "version": commit},
            {"part": "R Pathview", "version": r_pathview_report["environment"]["pathview_version"]},
            {"part": "R SBGNview", "version": r_sbgn_report["environment"]["SBGNview"]},
            {"part": "R", "version": r_sbgn_report["environment"]["r"]},
            {"part": "Bioconductor", "version": r_sbgn_report["environment"]["bioconductor"]},
        ])
        assert commit == "d4d45decec56e1ebec15cf04ae62ff944851780e"
        versions
        """
    ),
    md(
        """
        ## Same files and data

        I gave both programs the same hsa04110 files and the same small input
        tables. I also compared the file hashes before looking at the images.
        """
    ),
    code(
        """
        r_cache = RESULTS / "r-pathview" / "cache"
        input_checks = []
        for filename in ["hsa04110.xml", "hsa04110.png"]:
            python_file = FIXTURES / filename
            r_file = r_cache / filename
            input_checks.append({
                "file": filename,
                "same_sha256": sha256(python_file) == sha256(r_file),
                "sha256": sha256(python_file),
            })
        input_checks = pl.DataFrame(input_checks)
        assert input_checks["same_sha256"].all()
        input_checks
        """
    ),
    code(
        """
        shared_kegg = pl.read_csv(DATA / "hsa04110-shared-control-treatment.csv")
        shared_sbgn = pl.read_csv(DATA / "P00001-shared-control-treatment.csv")
        print("Shared KEGG input")
        display(shared_kegg)
        print("Shared SBGN input")
        display(shared_sbgn)
        """
    ),
    md(
        """
        ## Half-and-half test

        Each row is one gene. In this table `Low` is the first column, so it
        should appear on the left of a node. `High` is second, so it should be
        on the right. I used green for negative values, gray near zero, and red
        for positive values.
        """
    ),
    code(
        """
        strong = pl.read_csv(DATA / "hsa04110-strong-three-state.csv")
        half_data = strong.select("entrez", "Low", "High")

        scale = pv.ColorScale(
            limit=2.0, bins=11,
            low="#00FF00", mid="#BEBEBE", high="#FF0000",
            label="Gene log2 fold change",
        )

        half_result = pv.pathview(
            "04110",
            gene_data=half_data,
            species="hsa",
            kegg_dir=FIXTURES,
            out_dir=NOTEBOOK_RESULTS,
            out_suffix="live-half-half",
            render_mode="native",
            gene_color=scale,
            map_symbol=False,
            plot_col_key=False,
            new_signature=False,
            quiet=True,
        )

        live_raw = NOTEBOOK_RESULTS / "hsa04110.live-half-half.raw.png"
        half_result.save(live_raw)
        assert half_result.diagnostics["gene"].endswith("2/3 input IDs used")
        assert Image.open(live_raw).size == (1039, 801)
        print(half_result.summary())
        print("Raw image size:", Image.open(live_raw).size)
        display(NotebookImage(filename=str(live_raw), width=850))
        """
    ),
    md(
        """
        ## One, two, and three conditions

        These CDKN2A crops show that Python drew one whole color, two halves,
        and three bands in the right order.
        """
    ),
    code(
        """
        crop_dir = RESULTS / "python-pathview" / "figures"
        crop_paths = [
            crop_dir / "hsa04110.python-one-state.CDKN2A-crop.png",
            crop_dir / "hsa04110.python-half-half.CDKN2A-crop.png",
            crop_dir / "hsa04110.python-three-state.CDKN2A-crop.png",
        ]
        titles = ["One condition", "Two conditions", "Three conditions"]
        fig, axes = plt.subplots(1, 3, figsize=(12, 3))
        for axis, path, title in zip(axes, crop_paths, titles):
            axis.imshow(plt.imread(path), interpolation="nearest")
            axis.set_title(title)
            axis.axis("off")
        plt.tight_layout()
        plt.show()

        state_details = next(
            item["details"] for item in python_report["checks"] if item["id"] == "PY05"
        )
        pl.DataFrame([
            {
                "case": case,
                "condition_order": ", ".join(detail["states_in_order"]),
                "mapping": detail["mapped_gene_diagnostic"],
                "image_size": f"{detail['raw_output']['width_px']} x {detail['raw_output']['height_px']}",
            }
            for case, detail in state_details.items()
        ])
        """
    ),
    md(
        """
        ## R Pathview vs Pathview Plus

        Both programs used all five genes, put Control on the left and
        Treatment on the right, and kept the raw map at 1039 x 801. The images
        look close, but they are not pixel-for-pixel identical.
        """
    ),
    code(
        """
        shared_comparison = next(
            item["details"] for item in python_report["checks"] if item["id"] == "PY06"
        )
        display(NotebookImage(
            filename=str(RESULTS / "python-pathview" / "figures" /
                         "hsa04110.R-vs-Python.shared-side-by-side.png"),
            width=1000,
        ))
        print("IDs used by Python:", shared_comparison["used_ids"])
        print("Same dimensions:", shared_comparison["pixel_comparison"]["same_dimensions"])
        print("Identical-pixel fraction:",
              round(1 - shared_comparison["pixel_comparison"]["changed_pixel_fraction"], 4))
        print("Mean absolute channel difference out of 255:",
              shared_comparison["pixel_comparison"]["mean_absolute_channel_difference"])
        """
    ),
    md(
        """
        ## Genes and compounds

        I gave both programs the gene and compound table for hsa00020. The
        clearest difference in the saved image is the compound circle: R used
        an 8-pixel radius and Python used a 4-pixel radius.
        """
    ),
    code(
        """
        dual = next(item["details"] for item in python_report["checks"] if item["id"] == "PY08")
        display(NotebookImage(
            filename=str(RESULTS / "python-pathview" / "figures" /
                         "hsa00020.R-vs-Python.dual-omics-side-by-side.png"),
            width=1000,
        ))
        pl.DataFrame([
            {"data type": "Genes", "Python mapped rows": dual["gene_nodes_with_data"],
             "Python diagnostic": dual["gene_diagnostic"]},
            {"data type": "Compounds", "Python mapped rows": dual["compound_nodes_with_data"],
             "Python diagnostic": dual["compound_diagnostic"]},
        ])
        """
    ),
    md(
        """
        ## R SBGNview vs Pathview Plus

        In this run both programs used the seven shared genes, kept 83 arcs,
        and put Control on the left and Treatment on the right. R reports 78
        glyph objects together. Python reports 76 main glyphs plus two
        compartments, which adds to the same total.
        """
    ),
    code(
        """
        r_sbgn_png = RESULTS / "sbgnview" / "r-two-state_P00001.new.layout.sbgn.png"
        python_sbgn_png = RESULTS / "sbgnview" / "P00001.new.layout.python-two-state.png"
        show_pair(r_sbgn_png, python_sbgn_png, "R SBGNview 1.26.0", "Pathview Plus 3.1.0")

        sbgn_table = pl.DataFrame([
            {
                "check": "P00001 structure",
                "R SBGNview": "78 glyph objects; 83 arcs",
                "Pathview Plus": "76 primary + 2 compartments; 83 arcs",
            },
            {
                "check": "Namespaced file",
                "R SBGNview": "same signatures as bare file",
                "Pathview Plus": "same signatures as bare file",
            },
            {
                "check": "Shared IDs",
                "R SBGNview": "7/7 used",
                "Pathview Plus": "7/7 used",
            },
            {
                "check": "Colored gene/protein rows",
                "R SBGNview": "12/19 macromolecules",
                "Pathview Plus": "9/28 gene-class rows",
            },
            {
                "check": "Ports fixture",
                "R SBGNview": "ports, state, clone rendered",
                "Pathview Plus": "3/3 arcs; 2 through ports; state + clone kept",
            },
        ])
        sbgn_table
        """
    ),
    md(
        """
        ### The SBGN difference

        The programs made the same nine direct matches. R also used the
        SLC18A2 input to color three extra glyphs labeled VAT1. Python did not
        make those three extra matches. Python kept the state and clone data in
        its parsed result, but those marks were not drawn in the image.
        """
    ),
    md(
        """
        ## Test totals

        I list the package's own tests separately from the smaller checks I
        wrote for this comparison.
        """
    ),
    code(
        """
        upstream = next(item["details"] for item in python_report["checks"] if item["id"] == "PY02")
        r_counts = r_pathview_report["summary"]
        totals = pl.DataFrame([
            {
                "test group": "Pathview Plus upstream suite",
                "passed": upstream["passed"], "failed": upstream["failures"] + upstream["errors"],
                "skipped": upstream["skipped"],
            },
            {
                "test group": "My independent Python comparison",
                "passed": python_report["summary"]["passed"],
                "failed": python_report["summary"]["failed"], "skipped": 0,
            },
            {
                "test group": "My controlled R Pathview baseline",
                "passed": r_counts["passed"], "failed": r_counts["failed"],
                "skipped": r_counts["skipped"],
            },
            {
                "test group": "R/Python SBGN controlled assertions",
                "passed": sum(r_sbgn_report["assertions"].values()) +
                          sum(python_sbgn_report["assertions"].values()),
                "failed": 0, "skipped": 0,
            },
        ])
        totals
        """
    ),
    md(
        """
        ## What changed from August 10

        I went back through the 86 findings from August 10 with v3.1.0:

        - 60 are fixed.
        - 19 still happen.
        - 7 are handled differently in the new version.
        - 0 were left unchecked.

        The five bigger items still left involve
        `map_null`, native composed-image dimensions, multi-condition graph
        coloring, the Reactome download route, and symbol-label replacement.
        The detailed evidence is in `reports/V3-CHANGE-AUDIT.md`.

        I also found one small beginner input issue: a table containing an
        all-null row plus an unmatched ID can reach a mixed `str`/`None` sort.
        Dropping blank rows with `data.drop_nulls()` avoids it.
        """
    ),
    code(
        """
        v3_audit["counts"]
        """
    ),
    md(
        """
        ## My answer

        My short answer is that the new Python version handled the main cases
        I tried. The remaining differences are compound size, grouped KEGG
        rows, the SLC18A2/VAT1 mapping, and drawing state/clone marks. Those
        are the next checks I would make.
        """
    ),
    md(
        """
        ## Reproduce the full evidence

        From the repository root:

        ```bash
        cd 08-11-2026
        MPLBACKEND=Agg .venv/bin/python scripts/run_python_v3_comparison.py

        R_LIBS_USER="$PWD/../pygage-pathview-validation/.r-library" \
          Rscript scripts/run_r_pathview_comparison.R

        R_LIBS_USER="$PWD/../pygage-pathview-validation/.r-library" \
          Rscript scripts/run_sbgnview_comparison.R
        ```

        I saved the package versions, source commit, hashes, check results,
        images, and mapped-node tables under `results/`.
        """
    ),
]


notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {"display_name": "Python 3 (August 11 Pathview)",
                       "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": sys.version.split()[0]},
        "title": "R vs Python Pathview — my comparison",
    },
)

source_path = NOTEBOOKS / "01-pathview-v3-vs-r-and-sbgnview.ipynb"
executed_path = EXECUTED / "01-pathview-v3-vs-r-and-sbgnview.executed.ipynb"
nbf.validate(notebook)
nbf.write(notebook, source_path)

os.environ["PATH"] = str(DAY_ROOT / ".venv" / "bin") + os.pathsep + os.environ.get("PATH", "")
os.environ["IPYTHONDIR"] = str(DAY_ROOT / "cache" / "ipython")
os.environ["JUPYTER_DATA_DIR"] = str(DAY_ROOT / "cache" / "jupyter")
os.environ["MPLCONFIGDIR"] = str(DAY_ROOT / "cache" / "matplotlib")
os.environ["PATHVIEW_CACHE"] = str(DAY_ROOT / "cache" / "pathview-plus")

executed = copy.deepcopy(notebook)
client = NotebookClient(
    executed,
    timeout=300,
    kernel_name="python3",
    allow_errors=False,
    resources={"metadata": {"path": str(DAY_ROOT)}},
)
client.execute()
nbf.validate(executed)
nbf.write(executed, executed_path)

code_cells = [cell for cell in executed.cells if cell.cell_type == "code"]
error_outputs = [
    output
    for cell in code_cells
    for output in cell.get("outputs", [])
    if output.get("output_type") == "error"
]
unexecuted = [cell for cell in code_cells if cell.get("execution_count") is None]
report = {
    "source_notebook": str(source_path.relative_to(DAY_ROOT)),
    "executed_notebook": str(executed_path.relative_to(DAY_ROOT)),
    "code_cells": len(code_cells),
    "executed_code_cells": len(code_cells) - len(unexecuted),
    "unexecuted_code_cells": len(unexecuted),
    "error_outputs": len(error_outputs),
    "status": "pass" if not unexecuted and not error_outputs else "fail",
    "python": sys.version.split()[0],
    "pathview_plus": "3.1.0",
    "commit": "d4d45decec56e1ebec15cf04ae62ff944851780e",
}
(NOTEBOOKS / "execution-report.json").write_text(json.dumps(report, indent=2) + "\n")

if report["status"] != "pass":
    raise SystemExit(f"Notebook verification failed: {report}")

print(json.dumps(report, indent=2))
