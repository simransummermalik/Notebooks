#!/usr/bin/env python3
"""Create the beginner-friendly validation notebooks from versioned cell text."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT.parent / "08-10-2026" / "notebooks"
NOTEBOOKS.mkdir(parents=True, exist_ok=True)


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


def notebook(title: str, cells: list) -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "PyGAGE + Pathview validation",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.14"},
        "title": title,
    }
    return nb


setup_cell = code(
    """
    from pathlib import Path
    import json
    import os
    import sys

    HERE = Path.cwd().resolve()
    SEARCH_FOLDERS = (HERE, *HERE.parents)
    PROJECT_CANDIDATES = (
        *SEARCH_FOLDERS,
        *(folder / "pygage-pathview-validation" for folder in SEARCH_FOLDERS),
    )
    ROOT = next(
        (
            folder for folder in PROJECT_CANDIDATES
            if (folder / ".venv").exists() and (folder / "scripts").exists()
        ),
        HERE,
    )

    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
    print("Validation folder:", ROOT)
    """
)


start_cells = [
    md(
        """
        # Start here: PyGAGE and Pathview validation

        This notebook is the front page. It tells you what was tested and where to go next.

        You do **not** need to know R or Python before reading it. The detailed notebooks explain each table, each code block, and each output.
        """
    ),
    setup_cell,
    md(
        """
        ## The short answer

        - PyGAGE's classical paired analysis runs on the new repository data and matches the packaged R GAGE reference numbers.
        - Python Pathview Plus produces a normal one-color node when there is one condition.
        - With two conditions, both R pathview and Python Pathview Plus put the **first condition on the left** and the **second condition on the right**.
        - The controlled test uses `Classical = -2` and `Basal = +2`, so the expected node is green on the left and red on the right.
        """
    ),
    code(
        """
        import polars as pl

        def count_status(path):
            report = json.loads(path.read_text())
            statuses = [item["status"] for item in report["checks"]]
            return {
                "component": report["component"],
                "passed": statuses.count("pass"),
                "failed": statuses.count("fail"),
                "not_run": statuses.count("not_run"),
            }

        summary = pl.DataFrame([
            count_status(ROOT / "results" / "pygage" / "validation.json"),
            count_status(ROOT / "results" / "pathview_python" / "validation.json"),
            count_status(ROOT / "results" / "pathview_r" / "validation.json"),
        ])
        summary
        """
    ),
    md(
        """
        `not_run` means the test needs a fresh live KEGG download. The reproducible offline tests use the official KEGG files bundled with Bioconductor R pathview, so the most important single-state and half-and-half comparisons still run completely.
        """
    ),
    code(
        """
        from IPython.display import Image, display

        comparison_figure = ROOT / "results" / "comparison" / "r_vs_python_half_half.png"
        display(Image(filename=str(comparison_figure), width=1100))
        """
    ),
    md(
        """
        ## Open these next

        1. [01 — PyGAGE full validation](01_pygage_full_validation.ipynb)
        2. [02 — Pathview Plus full validation](02_pathview_plus_full_validation.ipynb)
        3. [03 — R pathview versus Python Pathview Plus](03_r_vs_python_pathview.ipynb)

        The complete written conclusion is in [`reports/FULL_VALIDATION_REPORT.md`](../reports/FULL_VALIDATION_REPORT.md).
        """
    ),
]


pygage_cells = [
    md(
        """
        # PyGAGE, explained from the beginning

        PyGAGE tests **groups of genes** instead of looking at only one gene at a time.

        A gene set can represent a pathway. If many genes in that pathway move together, PyGAGE can report that pathway as enriched.

        This notebook covers:

        1. a tiny example you can understand by looking at it;
        2. all three tests and both ways of combining results;
        3. the new large repository data table;
        4. saved charts, command-line outputs, and numerical R GAGE checks.
        """
    ),
    setup_cell,
    code(
        """
        import numpy as np
        import polars as pl
        import pygage
        from pygage import GAGEAnalysis, GAGEPreparation, load_gmt, read_matrix
        from pygage.visualization_utils import EnrichmentPlots
        from IPython.display import Image, display

        print("PyGAGE version:", pygage.__version__)
        print("Python version:", sys.version.split()[0])
        """
    ),
    md(
        """
        ## Part 1 — Read a very small expression table

        - Each **row** is one gene.
        - `control_1` and `control_2` are reference samples.
        - `treatment_1` and `treatment_2` are treatment samples.
        - Genes `g01` through `g10` were designed to increase.
        - Genes `g11` through `g20` were designed to decrease.
        """
    ),
    code(
        """
        expression = read_matrix(ROOT / "data" / "toy_expression.csv")
        gene_sets = load_gmt(ROOT / "data" / "toy_sets.gmt")
        print("Table shape (genes, columns):", expression.shape)
        expression.head(8)
        """
    ),
    md(
        """
        ## Part 2 — Turn expression into treatment-minus-control values

        PyGAGE uses positions starting at zero. Among the sample columns:

        - controls are positions `0` and `1`;
        - treatments are positions `2` and `3`.

        `comparison="paired"` subtracts each matched control from its matched treatment.
        """
    ),
    code(
        """
        prepared = GAGEPreparation.prepare_expression(
            expression,
            ref_indices=[0, 1],
            samp_indices=[2, 3],
            comparison="paired",
        )
        prepared.head(8)
        """
    ),
    md(
        """
        Positive numbers mean the treatment is higher. Negative numbers mean the treatment is lower.
        """
    ),
    code(
        """
        analysis = GAGEAnalysis()
        result = analysis.run_gage(
            prepared,
            gene_sets,
            set_size_range=(5, 50),
            test_method="t-test",
            meta_method="stouffer",
            compute_effect=True,
            leading_edge=True,
        )

        print("Top pathways that increased:")
        display(result["greater"].head())
        print("Top pathways that decreased:")
        display(result["less"].head())
        """
    ),
    md(
        """
        `p_val` measures evidence before multiple-testing correction. `q_val` is the Benjamini–Hochberg corrected value. Smaller values mean stronger evidence.
        """
    ),
    md(
        """
        ## Part 3 — Check every statistic/meta-method combination

        PyGAGE currently offers three gene-set tests:

        - **t-test:** compares the pathway mean with the background and includes variance;
        - **z-test:** a PAGE-style standardized mean comparison;
        - **KS test:** compares ranked distributions and is less tied to a normal-distribution assumption.

        It can combine sample-level evidence with:

        - **Stouffer:** combines normalized p-value scores;
        - **Fisher:** combines the logarithms of p-values.
        """
    ),
    code(
        """
        method_rows = []
        for test_method in ("t-test", "z-test", "ks-test"):
            for meta_method in ("stouffer", "fisher"):
                tested = GAGEAnalysis().run_gage(
                    prepared,
                    gene_sets,
                    set_size_range=(5, 50),
                    test_method=test_method,
                    meta_method=meta_method,
                )
                method_rows.append({
                    "test": test_method,
                    "combine": meta_method,
                    "top_greater": tested["greater"]["gene_set"][0],
                    "top_less": tested["less"]["gene_set"][0],
                    "tested_sets": tested["greater"].height,
                })
        pl.DataFrame(method_rows)
        """
    ),
    md(
        """
        ## Part 4 — What the PyGAGE charts mean

        - **Bubble plot:** one bubble per pathway. Horizontal position is the pathway statistic, color is significance, and bubble size is the number of genes.
        - **Enrichment heatmap:** compares pathway statistics across conditions.
        - **Running enrichment plot:** walks down a ranked gene list and shows where pathway genes cluster.
        - **Pathway gene-color chart:** gives every pathway gene a fold-change color that can be handed to a pathway renderer.
        """
    ),
    code(
        """
        bubble = ROOT / "results" / "pygage" / "toy_bubble.png"
        running = ROOT / "results" / "pygage" / "toy_running_enrichment.png"
        display(Image(filename=str(bubble), width=700))
        display(Image(filename=str(running), width=700))
        """
    ),
    md(
        """
        ## Part 5 — The new large repository data table

        The newest PyGAGE repository commit adds one file. It has 19,469 genes and 198 TCGA-style sample columns.

        The sample endings identify 184 `.01`, 13 `.11`, and one `.06` sample. The careful classical design uses the **13 patient-matched `.11`/`.01` pairs**. It does not incorrectly pair all 184 primary samples with 13 normal samples.

        The repository filename says `GDS3627`, but its columns use TCGA identifiers. Confirm the dataset's exact provenance before describing it in a publication.
        """
    ),
    code(
        """
        new_expression = read_matrix(
            ROOT / "data" / "upstream_pygage" / "GDS3627_exp_formatted.csv"
        )
        sample_columns = new_expression.columns[1:]

        def patient(sample):
            return ".".join(sample.split(".")[:3])

        primary = {
            patient(sample): sample
            for sample in sample_columns
            if sample.endswith(".01")
        }
        normal = [
            sample for sample in sample_columns
            if sample.endswith(".11") and patient(sample) in primary
        ]
        tumor = [primary[patient(sample)] for sample in normal]

        design = pl.DataFrame({
            "patient": [patient(sample) for sample in normal],
            "normal_reference": normal,
            "matched_primary_sample": tumor,
        })
        print("Expression shape:", new_expression.shape)
        print("Matched pairs:", design.height)
        design
        """
    ),
    code(
        """
        ref_indices = [sample_columns.index(sample) for sample in normal]
        samp_indices = [sample_columns.index(sample) for sample in tumor]

        new_prepared = GAGEPreparation.prepare_expression(
            new_expression,
            ref_indices=ref_indices,
            samp_indices=samp_indices,
            comparison="paired",
            input_logged=True,
        )
        upstream_sets = json.loads(
            (ROOT / "data" / "upstream_pygage" / "kegg_gs.json").read_text()
        )
        new_result = GAGEAnalysis().run_gage(
            new_prepared,
            upstream_sets,
            test_method="t-test",
            meta_method="stouffer",
        )
        print("Prepared shape:", new_prepared.shape)
        print("Top greater pathways:")
        display(new_result["greater"].head(8))
        print("Top less pathways:")
        display(new_result["less"].head(8))
        """
    ),
    code(
        """
        display(Image(
            filename=str(ROOT / "results" / "pygage" / "new_dataset_greater_bubble.png"),
            width=850,
        ))
        """
    ),
    md(
        """
        ## Part 6 — Numerical check against R GAGE

        The repository includes reference tables created by R GAGE. The validation joined pathways by name and checked t/Stouffer, z/Stouffer, and t/Fisher results.
        """
    ),
    code(
        """
        parity = pl.read_csv(ROOT / "results" / "pygage" / "r_gage_parity.csv")
        parity
        """
    ),
    md(
        """
        ## Part 7 — Command line checks

        These equivalent terminal workflows were also executed:

        ```bash
        pygage run data/toy_expression.csv -g data/toy_sets.gmt \
          -o results/pygage/cli_run.csv --ref 0,1 --samp 2,3 --min-size 5

        pygage go data/toy_annotations.gaf -o results/pygage/cli_go.json \
          --obo data/toy_go.obo --aspect BP --propagate

        pygage compare results/pygage/toy_greater.csv results/pygage/toy_less.csv \
          -o results/pygage/cli_compare.csv --names greater,less
        ```
        """
    ),
    code(
        """
        pl.read_csv(ROOT / "results" / "pygage" / "cli_run.csv").head()
        """
    ),
    md(
        """
        ## PyGAGE conclusion

        The main classical PyGAGE engine, supported inputs, six statistic/meta-method combinations, result helpers, general charts, three CLI workflows, new 13-pair data analysis, and packaged R GAGE numerical regressions all executed.

        See the full report for the exact test count and current compatibility notes.
        """
    ),
]


pathview_cells = [
    md(
        """
        # Pathview Plus, explained from the beginning

        Pathview Plus puts your numbers on top of a pathway diagram.

        The first column contains gene identifiers. Every later column is one condition or state.

        - One condition → one color across the node.
        - Two conditions → two vertical pieces: first column on the left, second column on the right.
        - Three conditions → three equal pieces from left to right.

        This notebook uses the official `hsa04110` KEGG files bundled with R pathview 1.52.0, so both implementations receive the exact same frozen pathway background.
        """
    ),
    setup_cell,
    code(
        """
        import importlib
        import shutil
        import numpy as np
        import polars as pl
        from PIL import Image as PILImage
        from IPython.display import Image, SVG, display
        import pathview
        from pathview import SpeciesInfo

        print("Pathview Plus distribution: 2.0.2")
        print("Runtime __version__:", pathview.__version__)
        """
    ),
    md(
        """
        ## Reproducible setup

        Current live pathway services can change. For a fair test, this notebook copies the frozen KEGG XML and PNG already installed with Bioconductor pathview.

        The small resolver below only prevents an unnecessary live organism-list request. It does not change the pathway data, mapping, color calculation, or renderer.
        """
    ),
    code(
        """
        CACHE = ROOT / "cache" / "kegg"
        CACHE.mkdir(parents=True, exist_ok=True)
        r_extdata = ROOT / ".r-library" / "pathview" / "extdata"
        for extension in ("xml", "png"):
            shutil.copy2(r_extdata / f"hsa04110.{extension}", CACHE / f"hsa04110.{extension}")

        orchestrator = importlib.import_module("pathview.pathview")
        original_resolver = orchestrator.kegg_species_code
        def frozen_human_resolver(species="hsa"):
            if species in {"hsa", "human", "Homo sapiens"}:
                return SpeciesInfo("hsa", True, None, None, None, None)
            return original_resolver(species)
        orchestrator.kegg_species_code = frozen_human_resolver

        palette = dict(
            limit={"gene": 2.0, "cpd": 2.0},
            bins={"gene": 11, "cpd": 11},
            both_dirs={"gene": True, "cpd": True},
            low={"gene": "#00FF00", "cpd": "#0000FF"},
            mid={"gene": "#BEBEBE", "cpd": "#BEBEBE"},
            high={"gene": "#FF0000", "cpd": "#FFFF00"},
        )
        """
    ),
    md(
        """
        ## Part 1 — The basic one-condition pathway

        `Classical` is the only value column, so every mapped node gets one full-width color.
        """
    ),
    code(
        """
        classical = pl.read_csv(
            ROOT / "data" / "classical_hsa04110.csv",
            schema_overrides={"gene_id": pl.String},
        )
        classical
        """
    ),
    code(
        """
        one_result = pathview.pathview(
            "04110",
            gene_data=classical,
            species="hsa",
            gene_idtype="ENTREZ",
            kegg_dir=CACHE,
            out_suffix="notebook_classical",
            map_symbol=False,
            new_signature=False,
            plot_col_key=False,
            **palette,
        )
        one_image = CACHE / "hsa04110.notebook_classical.png"
        display(Image(filename=str(one_image), width=800))
        """
    ),
    md(
        """
        ## Part 2 — The requested half-and-half pathway

        The order is important:

        1. `Classical` is first, so it goes on the **left**.
        2. `Basal` is second, so it goes on the **right**.

        Negative values use green and positive values use red in this controlled palette.
        """
    ),
    code(
        """
        half = pl.read_csv(
            ROOT / "data" / "half_and_half_hsa04110.csv",
            schema_overrides={"gene_id": pl.String},
        )
        half
        """
    ),
    code(
        """
        half_result = pathview.pathview(
            "04110",
            gene_data=half,
            species="hsa",
            gene_idtype="ENTREZ",
            kegg_dir=CACHE,
            out_suffix="notebook_half_half",
            map_symbol=False,
            new_signature=False,
            plot_col_key=False,
            **palette,
        )
        half_image = CACHE / "hsa04110.notebook_half_half.png"
        display(Image(filename=str(half_image), width=800))
        """
    ),
    code(
        """
        mapped = half_result["plot_data_gene"].filter(pl.col("Classical").is_not_null())
        mapped.select("entry_id", "name", "label", "x", "y", "Classical", "Basal")
        """
    ),
    md(
        """
        The table is the strongest first check: the expected values reached the expected pathway coordinates. The image test then checks color direction inside the CDKN2A node.
        """
    ),
    code(
        """
        half_check = json.loads(
            (ROOT / "results" / "pathview_python" / "validation.json").read_text()
        )
        pixel_check = next(
            item for item in half_check["checks"]
            if item["name"] == "exact half-and-half pixels on CDKN2A"
        )
        pl.DataFrame([pixel_check["details"]["pixel_counts"]])
        """
    ),
    md(
        """
        `left_green` and `right_red` are large, while `right_green` and `left_red` are zero. That is a direct pixel-level proof of the requested layout.
        """
    ),
    code(
        """
        display(Image(
            filename=str(ROOT / "results" / "pathview_python" / "hsa04110.half_half.raw_overlay.png"),
            width=800,
        ))
        """
    ),
    md(
        """
        ## Part 3 — Three conditions

        Three value columns make three equal left-to-right bands in the same column order.
        """
    ),
    code(
        """
        three = pl.read_csv(
            ROOT / "data" / "three_state_hsa04110.csv",
            schema_overrides={"gene_id": pl.String},
        )
        three_result = pathview.pathview(
            "04110",
            gene_data=three,
            species="hsa",
            gene_idtype="ENTREZ",
            kegg_dir=CACHE,
            out_suffix="notebook_three_state",
            map_symbol=False,
            new_signature=False,
            plot_col_key=False,
            **palette,
        )
        display(Image(filename=str(CACHE / "hsa04110.notebook_three_state.png"), width=800))
        """
    ),
    md(
        """
        ## Part 4 — Output formats

        The automated run checked:

        - native PNG;
        - SVG vector output;
        - graph-layout PDF.

        Python's native PNG and SVG split multiple states. Its graph/PDF renderer currently uses the first state only, so native PNG is the fair R/Python half-and-half comparison target.
        """
    ),
    code(
        """
        format_files = [
            ROOT / "results" / "pathview_python" / "hsa04110.half_half.png",
            ROOT / "results" / "pathview_python" / "hsa04110.half_half.svg",
            ROOT / "results" / "pathview_python" / "hsa04110.graph.pdf",
        ]
        pl.DataFrame({
            "file": [path.name for path in format_files],
            "exists": [path.exists() for path in format_files],
            "bytes": [path.stat().st_size for path in format_files],
        })
        """
    ),
    md(
        """
        ## Part 5 — Paper use cases ready for live KEGG access

        The validation package also includes prepared input tables for:

        - `hsa04151` PI3K–Akt, one classical condition;
        - `hsa04010` MAPK, three conditions;
        - `hsa00010` glycolysis, genes plus compounds;
        - `ko00910` nitrogen metabolism, KO identifiers.

        Run this after live KEGG access is available:

        ```bash
        python scripts/run_pathview_validation.py --live
        ```
        """
    ),
    md(
        """
        ## Pathview Plus conclusion

        The reproducible core run passed one-state, two-state, exact left/right pixels, three-state, PNG, SVG, and PDF checks on an official frozen pathway. The full report separates core behavior from live external-service checks and documents every tested public area.
        """
    ),
]


comparison_cells = [
    md(
        """
        # R pathview versus Python Pathview Plus

        This notebook answers one specific question fairly:

        > If R and Python receive the same pathway, genes, numbers, colors, and condition order, do they both make the requested left/right half-and-half node?

        Yes. The controlled native-PNG comparison passed.
        """
    ),
    setup_cell,
    md(
        """
        ## Part 1 — Execute both implementations

        R pathview and Python Pathview Plus use the same frozen `hsa04110.xml` and `hsa04110.png` from Bioconductor pathview 1.52.0.
        """
    ),
    code(
        """
        import subprocess
        import polars as pl
        from IPython.display import Image, display

        env = os.environ.copy()
        env["R_LIBS_USER"] = str(ROOT / ".r-library")
        subprocess.run(
            ["Rscript", str(ROOT / "scripts" / "run_r_pathview.R")],
            cwd=ROOT,
            env=env,
            check=True,
        )
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_pathview_validation.py")],
            cwd=ROOT,
            env=env,
            check=True,
        )
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "compare_r_python.py")],
            cwd=ROOT,
            env=env,
            check=True,
        )
        """
    ),
    code(
        """
        r_report = json.loads((ROOT / "results" / "pathview_r" / "validation.json").read_text())
        py_report = json.loads((ROOT / "results" / "pathview_python" / "validation.json").read_text())
        pl.DataFrame([
            {
                "implementation": "R pathview",
                "version": r_report["version"],
                "environment": r_report["r_version"],
            },
            {
                "implementation": "Python Pathview Plus",
                "version": py_report["distribution_version"],
                "environment": "Python " + py_report["python"],
            },
        ])
        """
    ),
    md(
        """
        ## Part 2 — Exact controlled input

        The input columns are deliberately ordered:

        | Position | Condition | Value for CDKN2A | Expected piece |
        |---:|---|---:|---|
        | 1 | Classical | -2 | left, green |
        | 2 | Basal | +2 | right, red |

        Explicit hex colors are important. R's named `green` and Matplotlib's named `green` are different shades even when both programs behave correctly.
        """
    ),
    code(
        """
        comparison = pl.read_csv(
            ROOT / "results" / "comparison" / "mapped_node_comparison.csv"
        )
        comparison
        """
    ),
    md(
        """
        The absolute differences are zero. Both tools mapped the same condition values to the same KEGG coordinates.
        """
    ),
    code(
        """
        display(Image(
            filename=str(ROOT / "results" / "comparison" / "r_vs_python_half_half.png"),
            width=1200,
        ))
        """
    ),
    md(
        """
        ## Part 3 — Pixel-direction proof

        Whole-image pixel identity is not required because the renderers handle PNG colors and output cropping differently. The robust check looks inside the same CDKN2A coordinates and asks where green and red pixels are concentrated.
        """
    ),
    code(
        """
        comparison_json = json.loads(
            (ROOT / "results" / "comparison" / "comparison.json").read_text()
        )
        orientation = comparison_json["pixel_orientation"]
        pl.DataFrame([
            {"implementation": "Python", **orientation["python_pixel_counts"]},
            {"implementation": "R", **orientation["r_pixel_counts"]},
        ])
        """
    ),
    md(
        """
        In both rows, left-green dominates right-green and right-red dominates left-red. That proves the same column order visually.
        """
    ),
    md(
        """
        ## Part 4 — What is the same and what is different?

        | Area | R pathview 1.52.0 | Python Pathview Plus 2.0.2 |
        |---|---|---|
        | One-state native PNG | Yes | Yes |
        | Two-state native PNG | Left/right bands | Left/right bands |
        | Three-state native PNG | Ordered bands | Ordered bands |
        | Graph/PDF multi-state | Yes | Uses first state only |
        | SVG output | Not a main pathview output | Yes, node-based SVG |
        | SBGN/non-KEGG integration | R pathview is KEGG-focused | Separate utilities exist; not yet end-to-end through `pathview()` |

        `split.group` in R is **not** the half-and-half feature. The half-and-half feature is `multi.state = TRUE` with two value columns.
        """
    ),
    md(
        """
        ## Final verdict

        For the requested basic classical example, use one value column. For the requested half-and-half view, use two columns in the order you want displayed.

        The controlled comparison passed at three levels:

        1. same mapped gene-node coordinates;
        2. identical state values at those coordinates;
        3. correct left-green/right-red pixel dominance in both R and Python.
        """
    ),
]


outputs = {
    "01_pygage_full_validation.ipynb": notebook("PyGAGE full validation", pygage_cells),
    "02_pathview_plus_full_validation.ipynb": notebook("Pathview Plus full validation", pathview_cells),
    "03_r_vs_python_pathview.ipynb": notebook("R versus Python pathview", comparison_cells),
}

for filename, nb in outputs.items():
    destination = NOTEBOOKS / filename
    nbf.write(nb, destination)
    print(f"Wrote {destination}")
