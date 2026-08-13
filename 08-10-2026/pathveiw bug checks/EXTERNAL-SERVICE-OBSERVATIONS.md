# External-service lab notes

**Checked:** August 10, 2026

I kept these notes separate from the offline test verdict because an external
service can change or temporarily go down even when the Pathview source has not
changed. The local URL construction, parsing, cache ordering, and error handling
are still reproducible code findings.

## KEGG

The [official KEGG API manual](https://www.kegg.jp/kegg/rest/keggapi.html)
documents `https://rest.kegg.jp/list/organism`, pathway KGML/image retrieval,
and the chemical `conv` routes.

Here is what I observed during the live check:

- On August 10, 2026, `https://rest.kegg.jp/list/organism` repeatedly returned
  HTTP 400 through both the execution environment and the web fetcher.
- Direct `hsa04110` KGML and image requests returned HTTP 200 during the
  separate live probe.
- The controlled chemical conversions also returned HTTP 200 during that
  separate live probe.

I am not labeling the HTTP 400 as a pure Pathview bug because it may have been a
provider-side incident or transition. The confirmed Pathview issue is that every
non-`ko` call depends on this lookup first, including a fully cached call that
already has a valid `hsa` code.

KEGG also asks clients to limit API use to three requests per second. The
compound mapper currently makes one request per ID without pacing or batching.

## MyGene.info

The [official batch-query documentation](https://docs.mygene.info/en/v3/doc/query_service.html#batch-queries-via-post)
specifies `POST https://mygene.info/v3/query`.

My live results were:

- The coded `/v3/querymany` route returned HTTP 404.
- The official `/v3/query` route returned HTTP 200 for a valid controlled
  request.
- The species values `hsa` and `Hs` were rejected. MyGene documents common
  species names for common organisms or taxonomy IDs.

I also found that nested results such as UniProt and Ensembl need structured
extraction. They should not be converted into a Python dictionary string.

## Reactome

The current code constructs
`/ContentService/exporter/sbgn/{id}.sbgn`, which returned HTTP 404.

Reactome's
[official content-service controller](https://github.com/reactome/content-service/blob/8d5b39fd903303163441ebf2ee3998a7c794bebe/src/main/java/org/reactome/server/service/controller/exporter/SbxxExporterController.java#L54-L61)
exposes `/ContentService/exporter/event/{id}.sbgn`. That route returned an SBGN
XML response in the separate live probe.

The [Reactome download page](https://reactome.org/download-data) also provides
human pathway diagrams as an SBGN archive, so it is a useful source for frozen
tests.

One additional code finding is that
`list_reactome_pathways(species=...)` hardcodes Homo sapiens in the URL. It only
changes the species label placed on the returned records.

## BioCyc / MetaCyc

The coded `?export=sbgn` page returned HTTP 404 with an HTML response.

The [official BioCyc web-services documentation](https://biocyc.org/web-services.shtml)
documents Pathway Tools XML and BioPAX services, not that automatic SBGN route.
The controlled `getxml` and BioPAX requests returned XML in the separate live
probe.

Until a supported SBGN source or a tested conversion is selected, the function
should not save an HTTP page as though it were a successful `.sbgn` file.

## PANTHER and SMPDB

Both current functions explicitly warn and return `None`. These are feature
gaps, not transient network failures.

[SMPDB's download area](https://smpdb.ca/downloads) and its pathway pages provide
an SBGN markup download route that can be implemented and frozen for tests.

The documentation examples also need to be verified:
[SMP0000001](https://smpdb.ca/view/SMP0000001) is Citrullinemia Type I, not
Glycolysis. PANTHER format and pathway examples should be checked against the
[official PANTHER user manual](https://pantherdb.org/help/PANTHER_user_manual.pdf)
before an automatic downloader is implemented.

## How I would rerun the live checks

I would keep the regular test run offline by using saved official examples and
controlled responses. Then I would run a smaller optional website check from
time to time and look at:

1. the status code and MIME type;
2. the XML root namespace or PNG signature;
3. one known ID and one intentionally missing ID;
4. provider rate limits and retry behavior;
5. the response schema before accepting a file or returning a mapping.
