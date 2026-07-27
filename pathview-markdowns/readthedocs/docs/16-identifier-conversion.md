# Convert gene and compound identifiers

*Page 16 of 24*

Use this page when the first column of your table contains gene or compound
identifiers that need to be connected to the identifiers used on a KEGG
pathway.

## The first column controls matching

Pathview Plus treats the first column as the identifier column. Every later
column is treated as a numeric measurement.

```text
source identifier -> target identifier -> pathway node -> color
```

For example, a gene-symbol table may begin like this:

| gene_symbol | log2_fold_change |
| --- | ---: |
| TP53 | -1.8 |
| EGFR | 2.4 |
| KRAS | 1.1 |

The setting below tells Pathview Plus how to interpret `gene_symbol`:

```python
gene_idtype="SYMBOL"
```

Keep all identifiers as strings, use one identifier system in the first
column, and place the measurement columns after it.

## Convert gene identifiers

| First column contains | Example | Pathview Plus setting | What happens before node matching |
| --- | --- | --- | --- |
| Entrez Gene IDs | `7157` | `gene_idtype="ENTREZ"` | IDs are used directly |
| gene symbols | `TP53` | `gene_idtype="SYMBOL"` | symbols are converted to Entrez IDs |
| Ensembl gene IDs | `ENSG00000141510` | `gene_idtype="ENSEMBL"` | Ensembl IDs are converted to Entrez IDs |
| UniProt accessions | `P04637` | `gene_idtype="UNIPROT"` | UniProt accessions are converted to Entrez IDs |
| direct KEGG gene IDs | the gene part after an organism prefix | `gene_idtype="KEGG"` | KEGG IDs are used directly |
| KEGG Orthology IDs | `K02586` | `gene_idtype="KEGG"` and `species="ko"` | KO IDs are used directly |

A direct KEGG pathway entry may be written with an organism prefix, such as
`eco:b0002`. In the input table, use the gene portion, such as `b0002`, and
choose the matching organism with `species="eco"`.

For KO data, use the complete `K` identifier:

```python
pathview(
    pathway_id="00910",
    species="ko",
    gene_data=ko_data,
    gene_idtype="KEGG",
)
```

Page 8 provides the complete
[KEGG Orthology tutorial](08-kegg-orthology.md).

## Let Pathview Plus convert gene IDs

For gene symbols, Ensembl IDs, UniProt accessions, and other conversion
categories, set `gene_idtype` in the main `pathview()` call. Pathview Plus
converts the first column to Entrez IDs before it matches the values to
pathway nodes. Entrez, direct KEGG, and KO IDs follow the direct-matching rows
in the table above.

```python
import polars as pl
from pathview import pathview

from pathview_setup import prepare_pathview


prepare_pathview()

symbol_data = pl.DataFrame(
    {
        "gene_symbol": ["TP53", "EGFR", "KRAS"],
        "log2_fold_change": [-1.8, 2.4, 1.1],
    }
)

pathview(
    pathway_id="04151",
    species="hsa",
    gene_data=symbol_data,
    gene_idtype="SYMBOL",
    map_symbol=False,
    kegg_dir="pathview_output",
    out_suffix="symbols",
)
```

The same pattern works with `gene_idtype="ENSEMBL"` or
`gene_idtype="UNIPROT"` when those identifiers occupy the first column.

If several source IDs connect to one target gene, `node_sum` chooses how their
values are combined. The default is:

```python
node_sum="sum"
```

The other available choices are `mean`, `median`, `max`, `max_abs`, and
`random`. Page 17 explains
[summarizing repeated mappings](17-simulate-and-summarize.md).

## Inspect gene conversion directly

Use `id2eg()` when you want to see the conversion table before drawing a
pathway. It returns a two-column Polars DataFrame containing the original IDs
and the Entrez Gene IDs supplied for them.

```python
from pathview import id2eg


symbol_map = id2eg(
    ["TP53", "EGFR", "KRAS"],
    category="SYMBOL",
    org="Hs",
)

print(symbol_map)
```

The same function accepts other gene identifier categories:

```python
ensembl_map = id2eg(
    ["ENSG00000141510", "ENSG00000146648"],
    category="ENSEMBL",
    org="Hs",
)

uniprot_map = id2eg(
    ["P04637", "P00533"],
    category="UNIPROT",
    org="Hs",
)

print(ensembl_map)
print(uniprot_map)
```

`org` identifies the organism used for the lookup. Examples include `Hs` for
human and `Mm` for mouse. Use the organism that produced your data.

## Convert Entrez IDs to another gene identifier

Use `eg2id()` when Entrez IDs are your starting point and you want a second
identifier system for review, labels, or another analysis.

```python
from pathview import eg2id


symbol_labels = eg2id(
    ["7157", "1956", "3845"],
    category="SYMBOL",
    org="Hs",
)

print(symbol_labels)
```

Common target categories include `SYMBOL`, `ENSEMBL`, and `UNIPROT`.
`eg2id()` returns a two-column Polars DataFrame whose first column is
`ENTREZID` and whose second column has the requested category name.

## Convert compound identifiers

Pathview Plus matches compounds through KEGG compound IDs. A KEGG compound ID
begins with `C`, such as `C00031`.

| First column contains | Setting | What happens before node matching |
| --- | --- | --- |
| KEGG compound IDs | `cpd_idtype="KEGG"` | IDs are used directly |
| PubChem IDs | `cpd_idtype="PUBCHEM"` | IDs are converted to KEGG compounds |
| ChEBI IDs | `cpd_idtype="CHEBI"` | IDs are converted to KEGG compounds |

For example:

```python
pathview(
    pathway_id="00010",
    species="hsa",
    cpd_data=compound_data,
    cpd_idtype="CHEBI",
    kegg_dir="pathview_output",
    out_suffix="chebi_compounds",
)
```

Page 9 provides the complete
[compound and multi-omics tutorials](09-compounds-and-multiomics.md).

## Inspect compound conversion directly

`cpd_id_map()` creates a two-column mapping table. The source type is set with
`in_type`, and the requested target type is set with `out_type`.

```python
from pathview import cpd_id_map


pubchem_to_kegg = cpd_id_map(
    ["3333"],
    in_type="PUBCHEM",
    out_type="KEGG",
)

chebi_to_kegg = cpd_id_map(
    ["17234"],
    in_type="CHEBI",
    out_type="KEGG",
)

print(pubchem_to_kegg)
print(chebi_to_kegg)
```

You can also begin with KEGG compound IDs and request another supported
identifier system:

```python
kegg_to_chebi = cpd_id_map(
    ["C00031"],
    in_type="KEGG",
    out_type="CHEBI",
)

print(kegg_to_chebi)
```

## Always review the returned mapping

Identifier records and cross-references are updated over time, so conversion
results reflect the selected species and the reference records available when
the code runs. Before using a conversion in a full analysis, print or save the
returned mapping and confirm:

1. the source column contains the IDs you submitted;
2. the target column contains the identifier system you requested;
3. the matched targets belong to the intended species;
4. blank target values are reviewed separately; and
5. repeated targets are combined with the `node_sum` method you intend to use.

This review makes the identifier step part of the analysis record and shows
exactly which rows can connect to pathway nodes.

## Identifier checklist

Before drawing the pathway, confirm that:

- the identifier column is the first column;
- every identifier is stored as text;
- one identifier system is used in that column;
- `gene_idtype` or `cpd_idtype` names that system;
- `species` matches the organism that produced the data; and
- a sample conversion table has been inspected.

[<- Previous: Choose output formats](15-output-formats.md) | [Home](index.md) | [Next: Simulate and summarize data ->](17-simulate-and-summarize.md)
