from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
from pathlib import Path

import polars as pl
import pytest

from conftest import FakeResponse
from pathview import (
    cpd_id_map,
    detect_database,
    download_kegg,
    download_metacyc,
    download_panther,
    download_reactome,
    download_smpdb,
    id2eg,
    kegg_species_code,
    list_reactome_pathways,
)


SOURCE_ROOT = Path(importlib.import_module("pathview").__file__).resolve().parent.parent
CLI_SOURCE = SOURCE_ROOT / "bin" / "pathview-cli.py"


def _load_cli_module():
    if not CLI_SOURCE.exists():
        pytest.skip(f"CLI source not found beside editable checkout: {CLI_SOURCE}")
    spec = importlib.util.spec_from_file_location("pathview_cli_audit", CLI_SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.cli
def test_cli_help_is_available() -> None:
    result = subprocess.run(
        [sys.executable, str(CLI_SOURCE), "--help"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--pathway-id" in result.stdout
    assert "--gene-data" in result.stdout
    assert "--cpd-data" in result.stdout
    assert "--output-format" in result.stdout


@pytest.mark.cli
def test_cli_rejects_invalid_output_choice() -> None:
    cli = _load_cli_module()
    with pytest.raises(SystemExit) as caught:
        cli.main(["--pathway-id", "04110", "--simulate", "--output-format", "jpg"])
    assert caught.value.code == 2


@pytest.mark.cli
def test_cli_requires_pathway_unless_legend(monkeypatch: pytest.MonkeyPatch) -> None:
    cli = _load_cli_module()
    with pytest.raises(SystemExit) as caught:
        cli.main([])
    assert caught.value.code == 2
    called: list[bool] = []
    monkeypatch.setattr(cli, "kegg_legend", lambda: called.append(True))
    cli.main(["--legend"])
    assert called == [True]


@pytest.mark.cli
def test_cli_gene_and_compound_tables_reach_core(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cli = _load_cli_module()
    gene_path = tmp_path / "genes.tsv"
    compound_path = tmp_path / "compounds.tsv"
    gene_path.write_text("id\tvalue\n1029\t1.0\n", encoding="utf-8")
    compound_path.write_text("id\tvalue\nC00031\t-1.0\n", encoding="utf-8")
    captured: dict = {}

    def fake_pathview(**kwargs):
        captured.update(kwargs)
        return {
            "plot_data_gene": pl.DataFrame({"entry_id": ["1"], "value": [1.0]}),
            "plot_data_cpd": pl.DataFrame({"entry_id": ["3"], "value": [-1.0]}),
        }

    monkeypatch.setattr(cli, "pathview", fake_pathview)
    cli.main(
        [
            "--pathway-id",
            "00001",
            "--gene-data",
            str(gene_path),
            "--cpd-data",
            str(compound_path),
        ]
    )
    assert captured["gene_data"]["id"].dtype == pl.String
    assert captured["cpd_data"].height == 1


@pytest.mark.cli
@pytest.mark.xfail(
    reason="PV-BUG-052: CLI unconditionally calls gene_data.cast even for compound-only input"
)
def test_cli_compound_only_workflow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cli = _load_cli_module()
    compound_path = tmp_path / "compounds.tsv"
    compound_path.write_text("id\tvalue\nC00031\t-1.0\n", encoding="utf-8")
    captured: dict = {}

    def fake_pathview(**kwargs):
        captured.update(kwargs)
        return {
            "plot_data_gene": None,
            "plot_data_cpd": pl.DataFrame({"entry_id": ["3"], "value": [-1.0]}),
        }

    monkeypatch.setattr(cli, "pathview", fake_pathview)
    cli.main(["--pathway-id", "00001", "--cpd-data", str(compound_path)])
    assert captured["gene_data"] is None
    assert captured["cpd_data"].height == 1


@pytest.mark.cli
@pytest.mark.xfail(
    reason="PV-BUG-077: --simulate branch silently ignores a supplied --cpd-data file"
)
def test_cli_simulation_can_be_combined_with_compound_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cli = _load_cli_module()
    compound_path = tmp_path / "compounds.tsv"
    compound_path.write_text("id\tvalue\nC00031\t-1.0\n", encoding="utf-8")
    monkeypatch.setattr(
        cli,
        "sim_mol_data",
        lambda **kwargs: pl.DataFrame({"id": ["1029"], "exp1": [1.0]}),
    )
    captured: dict = {}

    def fake_pathview(**kwargs):
        captured.update(kwargs)
        return {
            "plot_data_gene": pl.DataFrame({"entry_id": ["1"], "value": [1.0]}),
            "plot_data_cpd": pl.DataFrame({"entry_id": ["3"], "value": [-1.0]}),
        }

    monkeypatch.setattr(cli, "pathview", fake_pathview)
    cli.main(
        [
            "--simulate",
            "--pathway-id",
            "00001",
            "--cpd-data",
            str(compound_path),
        ]
    )
    assert captured["cpd_data"] is not None
    assert captured["cpd_data"].height == 1


@pytest.mark.cli
@pytest.mark.xfail(
    reason="PV-BUG-053: CLI reports pathway row count as 'nodes mapped', including null rows"
)
def test_cli_reports_non_null_mapped_count(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    cli = _load_cli_module()
    gene_path = tmp_path / "genes.tsv"
    gene_path.write_text("id\tvalue\n1029\t1.0\n", encoding="utf-8")
    monkeypatch.setattr(
        cli,
        "pathview",
        lambda **kwargs: {
            "plot_data_gene": pl.DataFrame(
                {"entry_id": ["1", "2", "3"], "value": [1.0, None, None]}
            ),
            "plot_data_cpd": None,
        },
    )
    cli.main(["--pathway-id", "00001", "--gene-data", str(gene_path)])
    assert "1 nodes mapped" in capsys.readouterr().out


@pytest.mark.cli
@pytest.mark.xfail(
    reason="PV-BUG-054: upstream feature script fails when run directly because of relative imports"
)
def test_upstream_feature_script_runs_as_documented() -> None:
    script = SOURCE_ROOT / "lib" / "test_all_features.py"
    if not script.exists():
        pytest.skip("upstream test_all_features.py not found")
    result = subprocess.run(
        [sys.executable, str(script)], text=True, capture_output=True, check=False
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.integration
def test_ko_species_resolution_is_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    kegg_module = importlib.import_module("pathview.kegg_api")
    monkeypatch.setattr(
        kegg_module.requests,
        "get",
        lambda *args, **kwargs: pytest.fail("KO lookup should not contact network"),
    )
    result = kegg_species_code("ko")
    assert result.kegg_code == "ko"
    assert result.entrez_gnodes is False


@pytest.mark.integration
def test_species_code_exact_match_is_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    kegg_module = importlib.import_module("pathview.kegg_api")
    response = FakeResponse(text="T01001\thsa\tHomo sapiens (human)\tEukaryotes;Animals")
    monkeypatch.setattr(kegg_module.requests, "get", lambda *args, **kwargs: response)
    assert kegg_species_code("HSA").kegg_code == "hsa"
    assert kegg_species_code("T01001").kegg_code == "hsa"


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-BUG-055: promised common-name lookup requires exact equality with full KEGG description"
)
def test_species_resolution_accepts_common_name(monkeypatch: pytest.MonkeyPatch) -> None:
    kegg_module = importlib.import_module("pathview.kegg_api")
    response = FakeResponse(text="T01001\thsa\tHomo sapiens (human)\tEukaryotes;Animals")
    monkeypatch.setattr(kegg_module.requests, "get", lambda *args, **kwargs: response)
    assert kegg_species_code("Homo sapiens").kegg_code == "hsa"
    assert kegg_species_code("human").kegg_code == "hsa"


@pytest.mark.integration
def test_kegg_download_builds_official_urls_and_writes_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kegg_module = importlib.import_module("pathview.kegg_api")
    urls: list[str] = []

    def fake_get(url, **kwargs):
        urls.append(url)
        if url.endswith("/kgml"):
            return FakeResponse(text='<pathway name="path:hsa00001" number="00001"/>')
        return FakeResponse(content=b"\x89PNG\r\n\x1a\ncontrolled")

    monkeypatch.setattr(kegg_module.requests, "get", fake_get)
    status = download_kegg("00001", species="hsa", kegg_dir=tmp_path)
    assert status == {"hsa00001": "succeed"}
    assert urls == [
        "https://rest.kegg.jp/get/hsa00001/kgml",
        "https://rest.kegg.jp/get/hsa00001/image",
    ]
    assert (tmp_path / "hsa00001.xml").exists()
    assert (tmp_path / "hsa00001.png").read_bytes().startswith(b"\x89PNG")


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-BUG-056: invalid KEGG file types fail with internal KeyError instead of validation error"
)
def test_kegg_download_rejects_invalid_file_type(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="file_type"):
        download_kegg("00001", kegg_dir=tmp_path, file_type=["pdf"])


@pytest.mark.integration
@pytest.mark.parametrize("file_type", ["xml", "png"])
@pytest.mark.xfail(
    reason="PV-BUG-057: KEGG downloader trusts any HTTP 200 body without format/content validation"
)
def test_kegg_download_rejects_html_error_page_with_status_200(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    file_type: str,
) -> None:
    kegg_module = importlib.import_module("pathview.kegg_api")
    html = "<html><title>temporary error</title></html>"
    monkeypatch.setattr(
        kegg_module.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(
            text=html, content=html.encode(), headers={"content-type": "text/html"}
        ),
    )
    status = download_kegg(
        "00001", species="hsa", kegg_dir=tmp_path, file_type=[file_type]
    )
    assert status == {"hsa00001": "failed"}
    assert not (tmp_path / f"hsa00001.{file_type}").exists()


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-BUG-058: MyGene batch endpoint is /v3/query, not coded /v3/querymany"
)
def test_mygene_uses_documented_batch_query_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    mapping_module = importlib.import_module("pathview.id_mapping")
    seen: dict = {}

    def fake_post(url, data, timeout):
        seen["url"] = url
        seen["data"] = data
        return FakeResponse(json_data=[{"query": "TP53", "entrezgene": 7157}])

    monkeypatch.setattr(mapping_module.requests, "post", fake_post)
    result = id2eg(["TP53"], category="SYMBOL", org="human")
    assert seen["url"] == "https://mygene.info/v3/query"
    assert result["ENTREZID"][0] == "7157"


@pytest.mark.integration
def test_mygene_notfound_result_becomes_null(monkeypatch: pytest.MonkeyPatch) -> None:
    mapping_module = importlib.import_module("pathview.id_mapping")
    monkeypatch.setattr(
        mapping_module.requests,
        "post",
        lambda *args, **kwargs: FakeResponse(
            json_data=[{"query": "missing", "notfound": True}]
        ),
    )
    result = id2eg(["missing"], category="SYMBOL", org="human")
    assert result["ENTREZID"][0] is None


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-BUG-059: nested MyGene fields are stringified as Python dicts instead of extracting IDs"
)
def test_mygene_nested_uniprot_result_extracts_accession(monkeypatch: pytest.MonkeyPatch) -> None:
    mapping_module = importlib.import_module("pathview.id_mapping")
    monkeypatch.setattr(
        mapping_module.requests,
        "post",
        lambda *args, **kwargs: FakeResponse(
            json_data=[
                {"query": "7157", "uniprot": {"Swiss-Prot": "P04637", "TrEMBL": ["A0A..."]}}
            ]
        ),
    )
    result = mapping_module.eg2id(["7157"], category="UNIPROT", org="human")
    assert result["UNIPROT"][0] == "P04637"


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-BUG-078: MyGene returnall dictionary response is iterated as if it were a list of hits"
)
def test_mygene_returnall_response_shape_is_supported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mapping_module = importlib.import_module("pathview.id_mapping")
    monkeypatch.setattr(
        mapping_module.requests,
        "post",
        lambda *args, **kwargs: FakeResponse(
            json_data={
                "out": [{"query": "TP53", "entrezgene": 7157}],
                "dup": [],
                "missing": [],
            }
        ),
    )
    result = id2eg(["TP53"], category="SYMBOL", org="human")
    assert result["ENTREZID"][0] == "7157"


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-BUG-060: core forwards KEGG code 'hsa' where MyGene documents common names/taxonomy IDs"
)
def test_symbol_mapping_translates_kegg_species_to_mygene_species(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mapping_module = importlib.import_module("pathview.id_mapping")
    seen: dict = {}

    def fake_post(url, data, timeout):
        seen.update(data)
        return FakeResponse(json_data=[{"query": "7157", "symbol": "TP53"}])

    monkeypatch.setattr(mapping_module.requests, "post", fake_post)
    mapping_module.eg2id(["7157"], category="SYMBOL", org="hsa")
    assert seen["species"] in {"human", "9606"}


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-BUG-061: KEGG chemical conversion uses alias 'cpd' where API specifies 'compound'"
)
def test_compound_mapping_uses_documented_kegg_database_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mapping_module = importlib.import_module("pathview.id_mapping")
    seen: list[str] = []

    def fake_get(url, **kwargs):
        seen.append(url)
        return FakeResponse(text="pubchem:123\tcpd:C00031")

    monkeypatch.setattr(mapping_module.requests, "get", fake_get)
    result = cpd_id_map(["123"], in_type="PUBCHEM", out_type="KEGG")
    assert seen == ["https://rest.kegg.jp/conv/compound/pubchem:123"]
    assert result["KEGG"][0] == "C00031"


@pytest.mark.integration
def test_compound_mapping_parses_controlled_kegg_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mapping_module = importlib.import_module("pathview.id_mapping")
    monkeypatch.setattr(
        mapping_module.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(text="pubchem:123\tcpd:C00031\n"),
    )
    result = cpd_id_map(["123"], in_type="PUBCHEM", out_type="KEGG")
    assert result.to_dict(as_series=False) == {"PUBCHEM": ["123"], "KEGG": ["C00031"]}


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-BUG-062: already-prefixed compound IDs receive a duplicate source prefix"
)
def test_compound_mapping_normalizes_prefixed_input(monkeypatch: pytest.MonkeyPatch) -> None:
    mapping_module = importlib.import_module("pathview.id_mapping")
    seen: list[str] = []

    def fake_get(url, **kwargs):
        seen.append(url)
        return FakeResponse(text="pubchem:123\tcpd:C00031")

    monkeypatch.setattr(mapping_module.requests, "get", fake_get)
    cpd_id_map(["pubchem:123"], in_type="PUBCHEM", out_type="KEGG")
    assert seen[0].endswith("/pubchem:123")
    assert "pubchem:pubchem" not in seen[0]


@pytest.mark.integration
@pytest.mark.parametrize(
    ("pathway_id", "expected"),
    [
        ("R-HSA-109582", "reactome"),
        ("PWY-7210", "metacyc"),
        ("P00001", "panther"),
        ("SMP0000001", "smpdb"),
        ("hsa04110", None),
        ("unknown", None),
    ],
)
def test_database_detection(pathway_id: str, expected: str | None) -> None:
    assert detect_database(pathway_id) == expected


@pytest.mark.integration
@pytest.mark.xfail(reason="PV-BUG-063: SMP prefix detection accepts malformed arbitrary IDs")
def test_database_detection_validates_smpdb_identifier() -> None:
    assert detect_database("SMPbanana") is None


@pytest.mark.integration
@pytest.mark.xfail(reason="PV-BUG-064: database detection is unexpectedly case-sensitive")
def test_database_detection_is_case_insensitive() -> None:
    assert detect_database("r-hsa-109582") == "reactome"


@pytest.mark.integration
def test_reactome_downloader_writes_controlled_sbgn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_module = importlib.import_module("pathview.databases")
    sbgn = '<sbgn xmlns="http://sbgn.org/libsbgn/0.2"><map id="m"/></sbgn>'
    monkeypatch.setattr(
        database_module.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(
            text=sbgn, headers={"content-type": "application/xml"}
        ),
    )
    output = download_reactome("R-HSA-109582", output_dir=tmp_path)
    assert output == tmp_path / "R-HSA-109582.sbgn"
    assert output.read_text() == sbgn


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-BUG-074: Reactome SBGN file exporter route is coded as /exporter/sbgn/{id}.sbgn instead of /exporter/event/{id}.sbgn"
)
def test_reactome_downloader_uses_file_exporter_route(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_module = importlib.import_module("pathview.databases")
    seen: list[str] = []

    def fake_get(url, **kwargs):
        seen.append(url)
        return FakeResponse(text='<sbgn><map id="m"/></sbgn>')

    monkeypatch.setattr(database_module.requests, "get", fake_get)
    download_reactome("R-HSA-109582", output_dir=tmp_path)
    assert seen == [
        "https://reactome.org/ContentService/exporter/event/R-HSA-109582.sbgn"
    ]


@pytest.mark.integration
@pytest.mark.parametrize("downloader,pathway_id", [(download_reactome, "R-HSA-109582"), (download_metacyc, "PWY-7210")])
@pytest.mark.xfail(
    reason="PV-BUG-065: SBGN downloaders accept HTTP 200 HTML pages as successful pathway files"
)
def test_sbgn_downloaders_reject_html(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    downloader,
    pathway_id: str,
) -> None:
    database_module = importlib.import_module("pathview.databases")
    monkeypatch.setattr(
        database_module.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(
            text="<html>login or error page</html>",
            headers={"content-type": "text/html"},
        ),
    )
    assert downloader(pathway_id, output_dir=tmp_path) is None
    assert not (tmp_path / f"{pathway_id}.sbgn").exists()


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-BUG-066: list_reactome_pathways hardcodes Homo sapiens in URL"
)
def test_reactome_listing_uses_requested_species(monkeypatch: pytest.MonkeyPatch) -> None:
    database_module = importlib.import_module("pathview.databases")
    seen: list[str] = []

    def fake_get(url, **kwargs):
        seen.append(url)
        return FakeResponse(json_data=[{"stId": "R-MMU-1", "displayName": "Mouse pathway"}])

    monkeypatch.setattr(database_module.requests, "get", fake_get)
    result = list_reactome_pathways("Mus musculus")
    assert "Mus%20musculus" in seen[0]
    assert result == [{"id": "R-MMU-1", "name": "Mouse pathway", "species": "Mus musculus"}]


@pytest.mark.integration
@pytest.mark.xfail(reason="PV-FEATURE-005: PANTHER downloader is an explicit unimplemented stub")
def test_panther_downloader_returns_path(tmp_path: Path) -> None:
    assert download_panther("P00001", output_dir=tmp_path) is not None


@pytest.mark.integration
@pytest.mark.xfail(reason="PV-FEATURE-006: SMPDB downloader is an explicit unimplemented stub")
def test_smpdb_downloader_returns_path(tmp_path: Path) -> None:
    assert download_smpdb("SMP0000001", output_dir=tmp_path) is not None


@pytest.mark.integration
@pytest.mark.xfail(
    reason="PV-FEATURE-007: non-KEGG database detection/download/parsing is not wired through pathview()"
)
def test_core_routes_reactome_ids_to_reactome_pipeline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    patch_hsa_species,
) -> None:
    core = importlib.import_module("pathview.pathview")
    called: list[str] = []
    monkeypatch.setattr(
        core,
        "download_kegg",
        lambda *args, **kwargs: called.append("kegg") or {"hsaR-HSA-109582": "failed"},
    )
    pathview_module = importlib.import_module("pathview.databases")
    monkeypatch.setattr(
        pathview_module,
        "download_reactome",
        lambda *args, **kwargs: called.append("reactome"),
    )
    import pathview as package

    package.pathview(
        "R-HSA-109582",
        gene_data=pl.DataFrame({"id": ["TP53"], "value": [1.0]}),
        species="hsa",
        kegg_dir=tmp_path,
        map_symbol=False,
    )
    assert called == ["reactome"]
