# Choose a pathway and species

*Page 5 of 14*

Pathview Plus needs a KEGG pathway number and a species code. Choose them from
the biological question behind your data.

## Begin with the biological question

Write the question in one sentence. For example:

```text
How do the genes in my treated human cells map to the PI3K-Akt pathway?
```

This sentence provides two choices:

- **PI3K-Akt signaling** suggests pathway `04151`.
- **human cells** suggests species `hsa`.

The Pathview Plus settings are:

```python
pathway_id="04151"
species="hsa"
```

## Find a KEGG pathway

Use the [KEGG PATHWAY database](https://www.kegg.jp/kegg/pathway.html) to browse
pathway names and numbers.

Follow these steps:

1. Open the KEGG PATHWAY link.
2. Choose the pathway category that matches your question, or use your
   browser's page search to find a pathway name.
3. Open the pathway entry.
4. Find its five-digit pathway number, such as `04151`.
5. Copy the five-digit number without a species prefix; the `species` setting
   will be added separately in the script.

Some examples used in this guide are:

| Pathway number | Name |
| --- | --- |
| `00010` | Glycolysis / Gluconeogenesis |
| `00910` | Nitrogen metabolism |
| `04010` | MAPK signaling pathway |
| `04110` | Cell cycle |
| `04151` | PI3K-Akt signaling pathway |
| `04512` | ECM-receptor interaction |

Always keep leading zeroes. Write `00910`, not `910`.

## Choose the species code

Common KEGG organism codes include:

| Organism or reference | Code |
| --- | --- |
| human | `hsa` |
| mouse | `mmu` |
| rat | `rno` |
| zebrafish | `dre` |
| fruit fly | `dme` |
| *C. elegans* | `cel` |
| budding yeast | `sce` |
| *E. coli* K-12 MG1655 | `eco` |
| thale cress | `ath` |
| KEGG Orthology reference | `ko` |

The [KEGG organism list](https://www.genome.jp/kegg/catalog/org_list.html)
contains additional organism codes.

## Match the code to the identifiers

Use this simple guide:

| Identifier table | Pathway choice | Species setting |
| --- | --- | --- |
| human Entrez Gene IDs | human pathway | `hsa` |
| mouse Entrez Gene IDs | mouse pathway | `mmu` |
| another organism's gene IDs | that organism's pathway | its KEGG code |
| KO IDs such as `K02586` | KO reference pathway | `ko` |
| human compounds | human metabolic pathway | `hsa` |

The pathway, species, and identifiers should describe the same biological
context.

## Use the pathway number in Python

The examples pass the number and species separately:

```python
pathview(
    pathway_id="04110",
    species="hsa",
    gene_data=gene_data,
    # more settings go here
)
```

Pathview Plus combines them into the full pathway name `hsa04110`.

For a KO reference pathway:

```python
pathview(
    pathway_id="00910",
    species="ko",
    gene_data=ko_data,
    # more settings go here
)
```

This becomes `ko00910`.

## A four-step selection checklist

1. Write the biological question.
2. Find the KEGG pathway that represents the process.
3. Choose the species or KO reference code.
4. Confirm that the first column of your table uses identifiers for that choice.

You now have everything needed for a full pathway run with your own file.

[<- Previous: Prepare your own data](04-prepare-your-data.md) | [Home](../README.md) | [Next: Map one gene measurement ->](06-one-gene-condition.md)
