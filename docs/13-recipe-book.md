# Recipe book

*Page 13 of 14*

Choose the row closest to your project and open its complete tutorial.

## Choose by input

| My first column contains | My numeric columns contain | Tutorial |
| --- | --- | --- |
| Entrez Gene IDs | one gene measurement | [Map one gene measurement](06-one-gene-condition.md) |
| Entrez Gene IDs | several conditions or time points | [Compare several gene conditions](07-multiple-gene-conditions.md) |
| KO IDs such as `K02586` | functional measurements | [Map KEGG Orthology data](08-kegg-orthology.md) |
| compound IDs such as `C00031` | compound measurements | [Map compounds](09-compounds-and-multiomics.md#part-a-map-compounds) |
| genes and compounds in two tables | one measurement for each data type | [Map genes and compounds together](09-compounds-and-multiomics.md#part-b-map-genes-and-compounds-together) |

## Choose by task

| I want to | Tutorial |
| --- | --- |
| make my first small example | [Make your first pathway](03-first-pathway.md) |
| load a TSV file | [Prepare your own data](04-prepare-your-data.md) |
| find a pathway and species code | [Choose a pathway and species](05-choose-a-pathway.md) |
| choose a color palette and limits | [Choose colors and read the image](10-colors-and-images.md) |
| make several pathway images | [Run several pathways](11-many-pathways.md) |
| work in Jupyter cells | [Use Pathview Plus in a notebook](12-use-a-notebook.md) |

## The table pattern for each recipe

### One gene measurement

```text
entrez_id | log2_fold_change
```

### Several gene conditions

```text
entrez_id | Control | Treatment_A | Treatment_B
```

### KO data

```text
ko_id | difference
```

### Compound data

```text
compound_id | log2_fold_change
```

## Four choices every recipe needs

Before running a recipe, write down:

1. **Data:** which table contains the IDs and values?
2. **Pathway:** which five-digit KEGG pathway number will you use?
3. **Species:** which organism code, or `ko`, matches the data?
4. **Output name:** what short suffix describes the analysis?

When those four choices are clear, open the matching tutorial and replace its
teaching values with your own.

[<- Previous: Use Pathview Plus in a notebook](12-use-a-notebook.md) | [Home](../README.md) | [Next: Glossary ->](14-glossary.md)
