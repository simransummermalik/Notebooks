# Before you begin

*Page 1 of 14*

This page introduces the five ideas used throughout the guide before the first
code example.

## What Pathview Plus does

Pathview Plus places your measurements on a KEGG pathway diagram.

It needs three main pieces of information:

1. a pathway;
2. biological identifiers; and
3. numerical values.

It uses those pieces to create a pathway image with colored genes or compounds.

```text
pathway + identifiers + values -> colored pathway image
```

## Idea 1: a pathway

A pathway is a diagram of biological parts and their relationships. A signaling
pathway can contain genes and proteins. A metabolic pathway can contain genes,
enzymes, reactions, and compounds.

In this guide, the pathway diagrams come from KEGG.

## Idea 2: a pathway ID

Each KEGG pathway has a number. Here are three examples:

| Pathway ID | Pathway name |
| --- | --- |
| `04151` | PI3K-Akt signaling pathway |
| `04110` | Cell cycle |
| `00910` | Nitrogen metabolism |

Keep the leading zero and place the ID inside quotes in Python.

```python
pathway_id="04151"
```

## Idea 3: a species code

A species code tells Pathview Plus which organism's pathway to use.

| Code | Meaning |
| --- | --- |
| `hsa` | human |
| `mmu` | mouse |
| `rno` | rat |
| `ath` | thale cress |
| `eco` | *E. coli* K-12 MG1655 |
| `ko` | KEGG Orthology reference pathway |

For a human pathway, you will usually combine a pathway number with
`species="hsa"`.

## Idea 4: a biological identifier

An identifier is a short, standardized name for a biological item.

| Identifier system | Example | Describes |
| --- | --- | --- |
| Entrez Gene | `1956` | a gene |
| KEGG Orthology | `K02586` | a shared biological function |
| KEGG compound | `C00031` | a compound |

The first column of a Pathview Plus table contains these identifiers.

## Idea 5: a numerical value

A value is the measurement you want to show with color. It could be log2 fold
change, a centered abundance value, a score, or another numeric result from
your analysis.

Here is a tiny gene table:

| entrez_id | log2_fold_change |
| --- | ---: |
| `7157` | -1.8 |
| `1956` | 2.4 |
| `3845` | 1.1 |

Read it like this:

- `entrez_id` tells Pathview Plus which gene to find;
- `log2_fold_change` tells Pathview Plus which color to use; and
- each row connects one identifier to one value.

## The workflow you will repeat

Every example in this guide follows the same six steps:

1. choose a KEGG pathway;
2. choose the matching species code;
3. prepare the identifier and value table;
4. load the table into Python;
5. run `pathview()`; and
6. open the finished pathway image.

Once this pattern feels familiar, the gene, KO, compound, and multi-condition
examples all become variations of the same workflow.

## Your first checkpoint

You are ready to continue if these statements make sense:

- a pathway ID selects the biological diagram;
- a species code selects the organism or KO reference;
- an identifier selects a gene, function, or compound; and
- a number becomes a color on the pathway.

[Home](../README.md) | [Next: Install Pathview Plus ->](02-install.md)
