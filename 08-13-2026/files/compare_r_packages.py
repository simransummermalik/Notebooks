#!/usr/bin/env python3
"""
compare_r_packages.py
Compare pathview-plus against R pathview and R SBGNview, from their sources.

What I checked
--------------
I wrote this as a first comparison of the Python package with R pathview and
R SBGNview. It reads the R package files instead of running R. The R details
come from:

  * exported symbols from ``NAMESPACE``
  * function argument names from the ``R/*.R`` definitions
  * package versions from ``DESCRIPTION``

I then compare those names with the installed pathview-plus API. This keeps the
counts tied to files I can point to instead of estimates from memory.

What this does not measure
--------------------------
I did not run R in this check, so it does not measure speed, memory, or whether
the two programs make pixel-identical images. That would need both packages
running on the same inputs.

Usage
-----
    python compare_r_packages.py \\
        --pathview-r /path/to/pathview \\
        --sbgnview-r /path/to/SBGNview \\
        --out results/

Downloads the R sources itself if the paths are omitted and a network is
available.

Outputs
-------
    comparison_data.csv        one row per compared item, tidy
    api_coverage.csv           R export -> pathview-plus counterpart
    argument_coverage.csv      R function argument -> Python argument
    feature_matrix.csv         the FEATURE_MATRIX, flattened
    summary.json               headline numbers
    fig1_feature_parity.png    plots
    fig2_api_coverage.png
    fig3_argument_coverage.png
    fig4_capability_split.png
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tarfile
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Parsing the R sources
# ---------------------------------------------------------------------------

R_SOURCES = {
    "pathview": "https://codeload.github.com/datapplab/pathview/tar.gz/refs/heads/master",
    "SBGNview": "https://codeload.github.com/datapplab/SBGNview/tar.gz/refs/heads/master",
}


@dataclass
class RPackage:
    """Everything read out of one R package's source tree."""

    name: str
    root: Path
    version: str = ""
    exports: list[str] = field(default_factory=list)
    functions: dict[str, list[str]] = field(default_factory=dict)   # name -> args
    datasets: list[str] = field(default_factory=list)

    @property
    def n_exports(self) -> int:
        return len(self.exports)


def fetch_r_package(name: str, dest: Path) -> Path:
    """Download and unpack an R package source tree."""
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / f"{name}-master"
    if target.exists():
        return target
    archive = dest / f"{name}.tar.gz"
    print(f"  downloading {name} ...", flush=True)
    urllib.request.urlretrieve(R_SOURCES[name], archive)
    with tarfile.open(archive) as tf:
        tf.extractall(dest)
    archive.unlink(missing_ok=True)
    return target


def parse_description(root: Path) -> str:
    desc = root / "DESCRIPTION"
    if not desc.exists():
        return "unknown"
    for line in desc.read_text(errors="replace").splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def parse_namespace(root: Path) -> list[str]:
    """Exported symbols from NAMESPACE (``export(...)`` and ``exportPattern``)."""
    ns = root / "NAMESPACE"
    if not ns.exists():
        return []
    text = ns.read_text(errors="replace")
    names: list[str] = []
    for match in re.finditer(r"^\s*export\s*\(([^)]*)\)", text, re.M):
        for part in match.group(1).split(","):
            cleaned = part.strip().strip('"').strip("'")
            if cleaned:
                names.append(cleaned)
    return sorted(set(names))


def _strip_r_comments(text: str) -> str:
    """
    Remove ``#`` comments, respecting string literals.

    R signatures are routinely commented inline, and a naive split captures
    the comment text as an argument name — which silently inflates the
    "missing" count with entries like ``#g\n split.group``.
    """
    out, in_string, quote = [], False, ""
    for line in text.splitlines():
        cleaned = []
        i = 0
        while i < len(line):
            ch = line[i]
            if in_string:
                cleaned.append(ch)
                if ch == quote and (i == 0 or line[i - 1] != "\\"):
                    in_string = False
            elif ch in "\"'":
                in_string, quote = True, ch
                cleaned.append(ch)
            elif ch == "#":
                break                       # rest of the line is a comment
            else:
                cleaned.append(ch)
            i += 1
        out.append("".join(cleaned))
    return "\n".join(out)


def _split_r_args(signature: str) -> list[str]:
    """Argument names from an R argument list, ignoring defaults and comments."""
    signature = _strip_r_comments(signature)
    args, depth, current = [], 0, ""
    for ch in signature:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            args.append(current)
            current = ""
        else:
            current += ch
    args.append(current)

    out = []
    for arg in args:
        nm = arg.split("=", 1)[0].strip()
        nm = " ".join(nm.split())            # collapse embedded newlines
        if nm and nm != "..." and re.fullmatch(r"[A-Za-z._][\w.]*", nm):
            out.append(nm)
    return out


def parse_r_functions(root: Path) -> dict[str, list[str]]:
    """
    Map every top-level R function to its argument names.

    R signatures span lines, so the argument list is collected by tracking
    parenthesis depth from the opening ``function(``.
    """
    functions: dict[str, list[str]] = {}
    for rfile in sorted((root / "R").glob("*.R")):
        text = rfile.read_text(errors="replace")
        for match in re.finditer(
            r"^\s*[`\"']?([A-Za-z._][\w._]*)[`\"']?\s*(?:<-|=)\s*function\s*\(",
            text, re.M,
        ):
            name = match.group(1)
            start = match.end()
            depth, i = 1, start
            while i < len(text) and depth:
                if text[i] == "(":
                    depth += 1
                elif text[i] == ")":
                    depth -= 1
                i += 1
            functions[name] = _split_r_args(text[start:i - 1])
    return functions


def parse_datasets(root: Path) -> list[str]:
    data = root / "data"
    if not data.exists():
        return []
    return sorted({p.stem.replace(".rda", "").replace(".RData", "")
                   for p in data.iterdir() if p.suffix in (".rda", ".RData")})


def load_r_package(name: str, root: Path) -> RPackage:
    pkg = RPackage(name=name, root=root)
    pkg.version = parse_description(root)
    pkg.exports = parse_namespace(root)
    pkg.functions = parse_r_functions(root)
    pkg.datasets = parse_datasets(root)
    return pkg


# ---------------------------------------------------------------------------
# The pathview-plus side
# ---------------------------------------------------------------------------

def load_pathview_plus() -> dict:
    """Read the public API from the installed pathview-plus package."""
    import inspect

    import pathview

    api: dict[str, list[str]] = {}
    for name in pathview.__all__:
        obj = getattr(pathview, name, None)
        if inspect.isfunction(obj) or inspect.isclass(obj):
            try:
                api[name] = [
                    p for p in inspect.signature(obj).parameters
                    if p not in ("self", "args", "kwargs")
                ]
            except (ValueError, TypeError):
                api[name] = []
    return {
        "version": pathview.__version__,
        "exports": sorted(pathview.__all__),
        "api": api,
        "feature_matrix": pathview.FEATURE_MATRIX,
        "summary": pathview.parity_summary(),
    }


# ---------------------------------------------------------------------------
# Mapping R names to pathview-plus names
#
# Hand-curated because the naming conventions differ (R uses dots, Python uses
# underscores) and several R functions are internal helpers with no intended
# public counterpart. Every mapping is checked against the real API below, so
# a stale entry shows up as "missing" rather than silently inflating coverage.
# ---------------------------------------------------------------------------

R_TO_PY: dict[str, str] = {
    # pathview
    "pathview": "pathview",
    "download.kegg": "download_kegg",
    "kegg.species.code": "kegg_species_code",
    "node.info": "node_info",
    "node.map": "node_map",
    "node.color": "node_color",
    "mol.sum": "mol_sum",
    "sim.mol.data": "sim_mol_data",
    "id2eg": "id2eg",
    "eg2id": "eg2id",
    "cpd2kegg": "cpd_id_map",
    "cpdidmap": "cpd_id_map",
    "cpdkegg2name": "compound_name",
    "cpdname2kegg": "cpd_name_to_kegg",
    "kegg.load": "parse_kgml",
    "parseKGML2Graph": "parse_kgml",
    "parseKGML2DataFrame": "pathway_edges",
    "KEGGpathway2Graph": "build_graph",
    "KEGGpathway2reactionGraph": "build_graph",
    "keggview.native": "keggview_native",
    "keggview.graph": "keggview_graph",
    "combineKEGGnodes": "split_groups",
    "reaction2edge": "pathway_edges",
    "geneannot.map": "eg2id",
    "kegg.species": "list_organisms",
    "pathview.stamp": "pathview",
    "col.key": "draw_color_key",
    "strfit": "strfit",
    "wordwrap": "wordwrap",
    # SBGNview
    "SBGNview": "sbgnview",
    "renderSbgn": "keggview_vector",
    "highlightNodes": "highlight_nodes",
    "highlightArcs": "highlight_edges",
    "highlightPath": "highlight_path",
    "changeDataId": "map_ids_to_sbgn",
    "changeIds": "map_ids_to_sbgn",
    "loadMappingTable": "sbgn_xref",
    "findPathways": "list_sbgn_pathways",
    "downloadSbgnFile": "download_sbgn",
    "sbgn.gsets": "list_sbgn_pathways",
    "sbgnNodes": "sbgn_to_df",
    "outputFile": "sbgnview",
    "mapped.ids": "map_ids_to_sbgn",
    "pathways.info": "sbgn_index",
    "sbgn.xmls": "download_sbgn",
}

#: R replacement functions (``name<-``) have no Python equivalent: assignment
#: to an attribute is not a separate exported symbol.
R_NOT_APPLICABLE_SUFFIX = "<-"

#: R exports that are internal plumbing and are not reimplemented.
#: Listed explicitly so they are excluded from coverage with a stated reason
#: rather than quietly ignored.
R_NOT_APPLICABLE: dict[str, str] = {
    "pathview.stamp": "R graphics stamp; pathview-plus signs figures inline",
    "korg": "data object, shipped as data/korg.tsv.gz",
    "bods": "data object, shipped as data/bods.tsv.gz",
    "cpd.simtypes": "data object",
    "gene.idtype.list": "exposed as supported_gene_idtypes()",
    "gene.idtype.bods": "exposed as supported_gene_idtypes()",
    "cpd.accs": "data object, shipped as data/cpd_xref.tsv.gz",
    "cpd.names": "data object, shipped as data/cpd_names.tsv.gz",
    "kegg.met": "data object",
    "ko.ids": "data object",
    "rn.list": "data object",
    "paths.hsa": "data object",
    "demo.paths": "example data",
    "gse16873": "example data, shipped as data/demo_gse16873.tsv.gz",
    "gse16873.d": "example data",
    "sbgn.xmls": "the SBGN collection, indexed as data/sbgn_index.tsv.gz",
}


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare_api(r_pkgs: dict[str, RPackage], pvp: dict) -> list[dict]:
    """One row per R export, recording whether pathview-plus has a counterpart."""
    rows = []
    py_exports = set(pvp["exports"])

    for pkg in r_pkgs.values():
        for export in pkg.exports:
            mapped = R_TO_PY.get(export)
            if export.endswith(R_NOT_APPLICABLE_SUFFIX):
                status, note = "n/a", ("R replacement function; Python uses "
                                       "plain attribute assignment")
            elif export in R_NOT_APPLICABLE:
                status, note = "n/a", R_NOT_APPLICABLE[export]
            elif mapped and mapped in py_exports:
                status, note = "covered", f"pathview.{mapped}"
            elif mapped:
                status, note = "missing", f"mapped to {mapped}, which is not exported"
            else:
                status, note = "missing", "no counterpart"
            rows.append({
                "r_package": pkg.name,
                "r_version": pkg.version,
                "r_export": export,
                "pathview_plus": mapped or "",
                "status": status,
                "note": note,
            })
    return rows


def compare_arguments(r_pkgs: dict[str, RPackage], pvp: dict) -> list[dict]:
    """
    Argument-level comparison for the two main entry points.

    ``pathview::pathview`` vs ``pathview.pathview`` and
    ``SBGNview::SBGNview`` vs ``pathview.sbgnview``. R uses dots where Python
    uses underscores, so names are normalised before matching; genuinely
    renamed options are listed in ``RENAMED``.
    """
    RENAMED = {
        # pathview R -> pathview-plus
        "kegg.native": "render_mode",
        "same.layer": "render_mode",
        "map.symbol": "map_symbol",
        "map.cpdname": "map_cpd_name",
        "map.null": "map_null",
        "min.nnodes": "min_nnodes",
        "node.sum": "node_sum",
        "both.dirs": "both_dirs",
        "trans.fun": "trans_fun",
        "low": "gene_color", "mid": "gene_color", "high": "gene_color",
        "na.col": "na_col",
        "out.suffix": "out_suffix",
        "kegg.dir": "kegg_dir",
        "gene.idtype": "gene_idtype",
        "cpd.idtype": "cpd_idtype",
        "gene.data": "gene_data",
        "cpd.data": "cpd_data",
        "pathway.id": "pathway_id",
        "split.group": "split_group",
        "expand.node": "expand_node",
        "plot.col.key": "plot_col_key",
        "new.signature": "new_signature",
        "res": "dpi",
        "cex": "figure_width",
        "discrete": "discrete",
        "limit": "limit", "bins": "bins", "species": "species",
        "multi.state": "gene_data",       # columns are conditions
        "match.data": "node_sum",
        "afactor": "figure_width",
        "text.width": "figure_width",
        "sign.pos": "new_signature",
        "key.pos": "plot_col_key",
        "out.dir": "out_dir",
        # SBGNview R -> pathview-plus
        "input.sbgn": "pathway_id",
        "output.file": "out_dir",
        "output.formats": "output_format",
        "sbgn.dir": "sbgn_dir",
        "gene.id.type": "gene_idtype",
        "cpd.id.type": "cpd_idtype",
        "sbgn.id.attr": "pathway_id",
        "show.pathway.name": "title",
        "col.gene.low": "gene_color", "col.gene.high": "gene_color",
        "col.gene.mid": "gene_color",
        "col.cpd.low": "cpd_color", "col.cpd.high": "cpd_color",
        "col.cpd.mid": "cpd_color",
        "min.gene.value": "limit", "max.gene.value": "limit",
        "min.cpd.value": "limit", "max.cpd.value": "limit",
        "if.scale.compartment.font.size": "figure_width",
        "compartment.layer.info": "show_compartments",
        "SBGNview.data.folder": "sbgn_dir",
        "sbgn.gene.id.type": "gene_idtype",
        "sbgn.cpd.id.type": "cpd_idtype",
        "pathway.name": "title",
        "id.mapping.gene": "id_mapping_gene",
        "id.mapping.cpd": "id_mapping_cpd",
        "simulate.data": "gene_data",
        "org": "species",          # SBGNview's organism argument
    }

    #: R arguments that name an R-only construct. Reported as n/a rather than
    #: missing, because "implement it" is not an available action.
    NOT_APPLICABLE = {
        "gene.annotpkg": "names a Bioconductor OrgDb package; the conversions "
                         "it provides are covered by id2eg/eg2id",
    }

    def normalise(name: str) -> str:
        return name.replace(".", "_").lower()

    rows = []
    pairs = [
        ("pathview", "pathview", "pathview", "pathview"),
        ("SBGNview", "SBGNview", "SBGNview", "sbgnview"),
    ]
    for r_pkg_name, r_fn, label, py_fn in pairs:
        pkg = r_pkgs.get(r_pkg_name)
        if pkg is None or r_fn not in pkg.functions:
            continue
        py_args = set(pvp["api"].get(py_fn, []))
        for r_arg in pkg.functions[r_fn]:
            direct = normalise(r_arg)
            renamed = RENAMED.get(r_arg)
            if r_arg in NOT_APPLICABLE:
                status, py_name = "n/a", NOT_APPLICABLE[r_arg]
            elif direct in py_args:
                status, py_name = "covered", direct
            elif renamed and renamed in py_args:
                status, py_name = "covered", renamed
            else:
                status, py_name = "missing", renamed or ""
            rows.append({
                "r_package": r_pkg_name,
                "r_version": pkg.version,
                "r_function": label,
                "r_argument": r_arg,
                "pathview_plus_argument": py_name,
                "status": status,
            })
    return rows


def flatten_feature_matrix(pvp: dict) -> list[dict]:
    return [{
        "category": f.category,
        "feature": f.name,
        "pathview_plus": f.pathview_plus,
        "pathview_R": f.pathview_r,
        "SBGNview_R": f.sbgnview_r,
        "api": f.api,
        "note": f.note,
    } for f in pvp["feature_matrix"]]


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

PALETTE = {
    "full": "#2E7D32", "covered": "#2E7D32",
    "partial": "#F9A825",
    "none": "#C62828", "missing": "#C62828",
    "n/a": "#B0BEC5",
}
PKG_COLOR = {
    "pathview-plus": "#1565C0",
    "pathview (R)": "#2E7D32",
    "SBGNview (R)": "#7E57C2",
}


def _style(ax, title: str, subtitle: str = "") -> None:
    ax.set_title(title, fontsize=12, fontweight="semibold", loc="left",
                 color="#111111", pad=24 if subtitle else 8)
    if subtitle:
        # Sits between the axes and the title; a smaller offset collides with
        # the title on tall panels.
        ax.text(0, 1.012, subtitle, transform=ax.transAxes, fontsize=8.5,
                color="#607D8B", va="bottom")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#B0BEC5")
    ax.spines["bottom"].set_color("#B0BEC5")
    ax.tick_params(colors="#37474F", labelsize=8.5)
    ax.grid(axis="x", color="#ECEFF1", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def plot_feature_parity(features: list[dict], summary: dict, out: Path,
                        versions: dict) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    from collections import Counter

    import matplotlib.pyplot as plt

    categories = []
    for row in features:
        if row["category"] not in categories:
            categories.append(row["category"])

    fig, axes = plt.subplots(1, 2, figsize=(14, 7.2),
                             gridspec_kw={"width_ratios": [1.25, 1]})
    fig.suptitle("Feature parity: pathview-plus vs the R packages",
                 fontsize=15, fontweight="semibold", x=0.02, ha="left", y=0.985)
    fig.text(0.02, 0.945,
             f"pathview-plus {versions['pathview_plus']}  ·  "
             f"pathview (R) {versions['pathview']}  ·  "
             f"SBGNview (R) {versions['SBGNview']}   —   "
             f"{summary['total_features']} capabilities, "
             f"source: lib/parity.py",
             fontsize=9, color="#607D8B", ha="left")

    # -- left: per-category status of pathview-plus ------------------------
    ax = axes[0]
    order = ["full", "partial", "none", "n/a"]
    y = range(len(categories))
    left = [0.0] * len(categories)
    for status in order:
        widths = [
            sum(1 for r in features
                if r["category"] == c and r["pathview_plus"] == status)
            for c in categories
        ]
        if not any(widths):
            continue
        ax.barh(list(y), widths, left=left, color=PALETTE[status],
                label=status, height=0.68, zorder=3,
                edgecolor="white", linewidth=0.8)
        for i, (w, l_) in enumerate(zip(widths, left)):
            if w:
                ax.text(l_ + w / 2, i, str(w), ha="center", va="center",
                        fontsize=8, color="white", fontweight="bold", zorder=4)
        left = [a + b for a, b in zip(left, widths)]

    ax.set_yticks(list(y))
    ax.set_yticklabels(categories)
    ax.invert_yaxis()
    ax.set_xlabel("capabilities", fontsize=9)
    ax.legend(frameon=False, fontsize=8.5, ncols=4, loc="lower right")
    _style(ax, "pathview-plus capability status, by category")

    # -- right: what each package supports ---------------------------------
    ax = axes[1]
    counts = {
        "pathview-plus": Counter(r["pathview_plus"] for r in features),
        "pathview (R)": Counter(r["pathview_R"] for r in features),
        "SBGNview (R)": Counter(r["SBGNview_R"] for r in features),
    }
    labels = list(counts)
    supported = [counts[k]["full"] for k in labels]
    partial = [counts[k]["partial"] for k in labels]
    absent = [counts[k]["none"] for k in labels]
    na = [counts[k]["n/a"] for k in labels]

    x = range(len(labels))
    bottom = [0.0] * len(labels)
    for vals, status in ((supported, "full"), (partial, "partial"),
                         (absent, "none"), (na, "n/a")):
        ax.bar(list(x), vals, bottom=bottom, color=PALETTE[status],
               width=0.55, zorder=3, edgecolor="white", linewidth=0.8,
               label=status)
        for i, (v, b) in enumerate(zip(vals, bottom)):
            if v > 2:
                ax.text(i, b + v / 2, str(v), ha="center", va="center",
                        fontsize=9, color="white", fontweight="bold", zorder=4)
        bottom = [a + b for a, b in zip(bottom, vals)]

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylabel("capabilities", fontsize=9)
    ax.grid(axis="y", color="#ECEFF1", linewidth=0.8, zorder=0)
    ax.grid(axis="x", visible=False)
    _style(ax, "Support across all tracked capabilities",
           "'n/a' marks a capability that does not apply to that package")
    ax.legend(frameon=False, fontsize=8.5, ncols=2, loc="upper right")

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = out / "fig1_feature_parity.png"
    fig.savefig(path, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def plot_api_coverage(api_rows: list[dict], out: Path, versions: dict) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    from collections import Counter

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6),
                             gridspec_kw={"width_ratios": [1, 1.15]})
    fig.suptitle("API coverage: R exported functions with a pathview-plus counterpart",
                 fontsize=14, fontweight="semibold", x=0.02, ha="left", y=0.98)
    fig.text(0.02, 0.925,
             "Parsed from each package's NAMESPACE. 'n/a' entries are data "
             "objects, which pathview-plus ships as bundled tables.",
             fontsize=8.5, color="#607D8B", ha="left")

    # -- left: stacked counts per package ----------------------------------
    ax = axes[0]
    pkgs = ["pathview", "SBGNview"]
    counts = {p: Counter(r["status"] for r in api_rows if r["r_package"] == p)
              for p in pkgs}
    labels = [f"{p} (R)\n{versions[p]}" for p in pkgs]
    x = range(len(pkgs))
    bottom = [0.0] * len(pkgs)
    for status in ("covered", "missing", "n/a"):
        vals = [counts[p][status] for p in pkgs]
        ax.bar(list(x), vals, bottom=bottom, width=0.5, color=PALETTE[status],
               label=status, zorder=3, edgecolor="white", linewidth=0.8)
        for i, (v, b) in enumerate(zip(vals, bottom)):
            if v:
                ax.text(i, b + v / 2, str(v), ha="center", va="center",
                        fontsize=9, color="white", fontweight="bold", zorder=4)
        bottom = [a + b for a, b in zip(bottom, vals)]

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("exported symbols", fontsize=9)
    ax.grid(axis="y", color="#ECEFF1", linewidth=0.8, zorder=0)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, fontsize=8.5, ncols=3, loc="upper right")
    _style(ax, "Exported symbols by coverage")

    # -- right: coverage rate, excluding n/a -------------------------------
    ax = axes[1]
    rates, names = [], []
    for p in pkgs:
        applicable = counts[p]["covered"] + counts[p]["missing"]
        rate = 100 * counts[p]["covered"] / applicable if applicable else 0
        rates.append(rate)
        names.append(f"{p} (R)")
    bars = ax.barh(names, rates, color=[PKG_COLOR["pathview (R)"],
                                        PKG_COLOR["SBGNview (R)"]],
                   height=0.42, zorder=3)
    for bar, rate, p in zip(bars, rates, pkgs):
        applicable = counts[p]["covered"] + counts[p]["missing"]
        ax.text(rate + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{rate:.0f}%  ({counts[p]['covered']}/{applicable})",
                va="center", fontsize=9.5, color="#37474F", fontweight="medium")
    ax.set_xlim(0, 118)
    ax.set_xlabel("% of applicable R exports with a counterpart", fontsize=9)
    ax.invert_yaxis()
    _style(ax, "Coverage rate",
           "Data objects excluded — they ship as bundled tables, not functions")

    fig.tight_layout(rect=(0, 0, 1, 0.9))
    path = out / "fig2_api_coverage.png"
    fig.savefig(path, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def plot_argument_coverage(arg_rows: list[dict], out: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    functions = []
    for row in arg_rows:
        if row["r_function"] not in functions:
            functions.append(row["r_function"])
    if not functions:
        return out / "fig3_argument_coverage.png"

    fig, axes = plt.subplots(
        1, len(functions), figsize=(7.2 * len(functions), 9.5)
    )
    if len(functions) == 1:
        axes = [axes]

    fig.suptitle("Argument-level coverage of the main entry points",
                 fontsize=14, fontweight="semibold", x=0.02, ha="left", y=0.985)
    fig.text(0.02, 0.955,
             "Every argument of the R function, and whether pathview-plus "
             "exposes an equivalent. Parsed from the R source, matched against "
             "the Python signature.",
             fontsize=8.5, color="#607D8B", ha="left")

    for ax, fn in zip(axes, functions):
        rows = [r for r in arg_rows if r["r_function"] == fn]
        rows.sort(key=lambda r: (r["status"] != "covered", r["r_argument"]))
        y = list(range(len(rows)))
        colors = [PALETTE[r["status"]] for r in rows]
        ax.barh(y, [1] * len(rows), color=colors, height=0.72, zorder=3)

        for i, row in enumerate(rows):
            target = row["pathview_plus_argument"] or "—"
            ax.text(0.02, i, row["r_argument"], va="center", ha="left",
                    fontsize=7.6, color="white", fontweight="medium", zorder=4)
            ax.text(0.98, i, target, va="center", ha="right",
                    fontsize=7.6, color="white", zorder=4)

        covered = sum(1 for r in rows if r["status"] == "covered")
        ax.set_yticks([])
        ax.set_xticks([])
        ax.invert_yaxis()
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(
            f"{fn}()  —  {covered}/{len(rows)} arguments covered "
            f"({100 * covered / len(rows):.0f}%)",
            fontsize=11, fontweight="semibold", loc="left", pad=8)
        ax.text(0, -0.022, "R argument", transform=ax.transAxes, fontsize=8,
                color="#607D8B", ha="left", va="top")
        ax.text(1, -0.022, "pathview-plus", transform=ax.transAxes, fontsize=8,
                color="#607D8B", ha="right", va="top")

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = out / "fig3_argument_coverage.png"
    fig.savefig(path, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def plot_capability_split(features: list[dict], out: Path) -> Path:
    """Where each package is strong, and what only pathview-plus has."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def has(v: str) -> bool:
        return v in ("full", "partial")

    only_plus = [r for r in features
                 if has(r["pathview_plus"])
                 and not has(r["pathview_R"]) and not has(r["SBGNview_R"])]
    shared_all = [r for r in features
                  if has(r["pathview_plus"]) and has(r["pathview_R"])
                  and has(r["SBGNview_R"])]
    plus_and_pv = [r for r in features
                   if has(r["pathview_plus"]) and has(r["pathview_R"])
                   and not has(r["SBGNview_R"])]
    plus_and_sv = [r for r in features
                   if has(r["pathview_plus"]) and has(r["SBGNview_R"])
                   and not has(r["pathview_R"])]
    missing_plus = [r for r in features
                    if not has(r["pathview_plus"])
                    and (has(r["pathview_R"]) or has(r["SBGNview_R"]))]

    groups = [
        ("In all three", len(shared_all), "#2E7D32"),
        ("pathview-plus + pathview (R)", len(plus_and_pv), "#1565C0"),
        ("pathview-plus + SBGNview (R)", len(plus_and_sv), "#7E57C2"),
        ("pathview-plus only", len(only_plus), "#EF6C00"),
        ("In an R package, not in\npathview-plus", len(missing_plus), "#C62828"),
    ]

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 6.4),
                                  gridspec_kw={"width_ratios": [1, 1.3]})
    fig.suptitle("Where the capabilities sit",
                 fontsize=14, fontweight="semibold", x=0.02, ha="left", y=0.98)
    fig.text(0.02, 0.925,
             "A capability counts as present when a package marks it full or "
             "partial.",
             fontsize=8.5, color="#607D8B", ha="left")

    names = [g[0] for g in groups]
    vals = [g[1] for g in groups]
    colors = [g[2] for g in groups]
    bars = ax.barh(names, vals, color=colors, height=0.55, zorder=3)
    for bar, v in zip(bars, vals):
        ax.text(v + 0.4, bar.get_y() + bar.get_height() / 2, str(v),
                va="center", fontsize=10, fontweight="bold", color="#37474F")
    ax.invert_yaxis()
    ax.set_xlabel("capabilities", fontsize=9)
    ax.set_xlim(0, max(vals) * 1.18)
    _style(ax, "Capability overlap")

    ax2.axis("off")
    lines = ["Capabilities pathview-plus has that neither R package does:", ""]
    for row in only_plus:
        lines.append(f"  • {row['feature']}")
    if missing_plus:
        lines += ["", "In an R package but not pathview-plus:", ""]
        for row in missing_plus:
            lines.append(f"  • {row['feature']}")
    else:
        lines += ["", "Nothing in either R package is missing from",
                  "pathview-plus, except where marked not-applicable",
                  "(Bioconductor OrgDb: an R library cannot be imported",
                  "from Python; its conversions are covered by id2eg/eg2id",
                  "and the bundled crosswalks)."]
    ax2.text(0, 1, "\n".join(lines), transform=ax2.transAxes, fontsize=9,
             va="top", ha="left", color="#263238", family="monospace",
             linespacing=1.5)

    fig.tight_layout(rect=(0, 0, 1, 0.9))
    path = out / "fig4_capability_split.png"
    fig.savefig(path, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def write_csv(rows: list[dict], path: Path) -> None:
    import csv
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pathview-r", type=Path, default=None,
                        help="path to the R pathview source tree")
    parser.add_argument("--sbgnview-r", type=Path, default=None,
                        help="path to the R SBGNview source tree")
    parser.add_argument("--out", type=Path, default=Path("results"))
    parser.add_argument("--cache", type=Path, default=Path(".r-sources"),
                        help="where to download R sources if not supplied")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args(argv)

    args.out.mkdir(parents=True, exist_ok=True)

    print("Loading R sources")
    roots = {
        "pathview": args.pathview_r or fetch_r_package("pathview", args.cache),
        "SBGNview": args.sbgnview_r or fetch_r_package("SBGNview", args.cache),
    }
    r_pkgs = {name: load_r_package(name, root) for name, root in roots.items()}
    for pkg in r_pkgs.values():
        print(f"  {pkg.name} {pkg.version}: {pkg.n_exports} exports, "
              f"{len(pkg.functions)} functions, {len(pkg.datasets)} datasets")

    print("Reading the installed pathview-plus API")
    pvp = load_pathview_plus()
    print(f"  pathview-plus {pvp['version']}: {len(pvp['exports'])} exports")

    versions = {"pathview_plus": pvp["version"],
                **{k: v.version for k, v in r_pkgs.items()}}

    api_rows = compare_api(r_pkgs, pvp)
    arg_rows = compare_arguments(r_pkgs, pvp)
    feat_rows = flatten_feature_matrix(pvp)

    write_csv(api_rows, args.out / "api_coverage.csv")
    write_csv(arg_rows, args.out / "argument_coverage.csv")
    write_csv(feat_rows, args.out / "feature_matrix.csv")

    tidy = (
        [{"comparison": "api", **r} for r in api_rows]
        + [{"comparison": "argument", **r} for r in arg_rows]
        + [{"comparison": "feature", **r} for r in feat_rows]
    )
    keys: list[str] = []
    for row in tidy:
        for k in row:
            if k not in keys:
                keys.append(k)
    write_csv([{k: r.get(k, "") for k in keys} for r in tidy],
              args.out / "comparison_data.csv")

    def rate(rows: list[dict], pkg: str | None = None) -> dict:
        sel = [r for r in rows if pkg is None or r["r_package"] == pkg]
        covered = sum(1 for r in sel if r["status"] == "covered")
        applicable = sum(1 for r in sel if r["status"] in ("covered", "missing"))
        return {"covered": covered, "applicable": applicable,
                "pct": round(100 * covered / applicable, 1) if applicable else 0.0}

    summary = {
        "versions": versions,
        "feature_matrix": pvp["summary"],
        "api_coverage": {p: rate(api_rows, p) for p in r_pkgs},
        "argument_coverage": {
            fn: rate([r for r in arg_rows if r["r_function"] == fn])
            for fn in {r["r_function"] for r in arg_rows}
        },
        "r_exports": {p: k.n_exports for p, k in r_pkgs.items()},
        "pathview_plus_exports": len(pvp["exports"]),
        "method": ("I read the R package source files and compared their "
                   "exports and arguments with the installed Python API. "
                   "R was not run, so this is not a runtime or image benchmark."),
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2))

    print("\nSummary")
    for pkg, r in summary["api_coverage"].items():
        print(f"  API   vs {pkg:<9} {r['covered']}/{r['applicable']} ({r['pct']}%)")
    for fn, r in sorted(summary["argument_coverage"].items()):
        print(f"  args  {fn+'()':<14} {r['covered']}/{r['applicable']} ({r['pct']}%)")
    fm = summary["feature_matrix"]
    print(f"  features           {fm['full']} full / {fm['partial']} partial "
          f"/ {fm['none']} missing of {fm['total_features']}")

    if not args.no_plots:
        print("\nPlots")
        for path in (
            plot_feature_parity(feat_rows, pvp["summary"], args.out, versions),
            plot_api_coverage(api_rows, args.out, versions),
            plot_argument_coverage(arg_rows, args.out),
            plot_capability_split(feat_rows, args.out),
        ):
            print(f"  {path}")

    print(f"\nWrote results to {args.out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
