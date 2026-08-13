# Understand gene sets

*Page 9 of 31*

A gene set is a named group of related gene identifiers. PyGAGE tests whether
the values for those members differ from the measured-gene background.

This page follows the gene-set input rules in PyGAGE 1.2.1.

## The required structure

```text
gene-set name -> list of member gene IDs
```

In Python, this is a dictionary:

```python
gene_sets = {
    "Growth pathway": ["1", "2", "3", "4"],
    "Stress pathway": ["7", "8", "9", "10"],
}
```

The names label result rows. The lists define membership.

## 1. Create `gene_sets.json`

Create a plain-text file named `gene_sets.json`:

```json
{
  "Growth pathway": ["1", "2", "3", "4"],
  "Stress pathway": ["7", "8", "9", "10"],
  "Mixed pathway": ["3", "5", "8", "11"]
}
```

JSON stores the same name-to-list structure outside Python. Its syntax rules
are:

- text uses double quotation marks;
- commas separate list members and sets;
- square brackets contain a member list; and
- curly braces contain the whole collection.

## 2. Check identifier matching

Create `check_gene_sets.py`:

```python
import json
from pathlib import Path

from pygage import read_matrix


expression = read_matrix("expression.csv")
gene_sets = json.loads(
    Path("gene_sets.json").read_text()
)

measured = set(expression["gene_id"].to_list())

print("Measured genes:", len(measured))
print("Gene sets:", len(gene_sets))

for set_name, members in gene_sets.items():
    matched = [gene for gene in members if gene in measured]
    print(
        set_name,
        "listed =", len(members),
        "matched =", len(matched),
    )
```

Run:

```bash
python check_gene_sets.py
```

Each teaching set reports four listed and four matched genes.

## Identifier matching is exact

These pairs are different text:

```text
TP53     versus  7157
ENSG00000141510  versus  TP53
hsa:7157         versus  7157
```

Choose one identifier system and use it on both sides:

```text
expression gene_id <-> gene-set member ID
```

The high-level input loader stores measurement IDs as text. PyGAGE also
stringifies and de-duplicates gene-set members while preserving their order.

## Missing and repeated members

During analysis:

- gene-set members absent from the measurement table are ignored;
- repeated members count once; and
- `set_size` reports the number of unique members found in the data.

The original collection is not changed.

## Set-size filtering

The standard analysis default is:

```python
set_size_range=(10, 500)
```

A set is tested only when 10 through 500 of its members are present in the
measurement table. The limits are inclusive.

The teaching collection contains only four members per set, so pages 10–14 use:

```python
set_size_range=(2, 10)
```

Keep the standard default for a real collection unless the analysis plan
justifies another range.

## Accepted collection types

The analysis engine accepts either:

1. a normal mapping such as the dictionary loaded from JSON; or
2. a `GeneSetCollection`, which adds source, release, retrieval date, and
   checksum metadata.

The complete canonical-conversion helper is:

```python
from pygage.gene_sets import normalize_gene_sets

canonical = normalize_gene_sets(gene_sets)
```

It returns:

```text
dict[str, list[str]]
```

Pages 15–18 show how PyGAGE obtains KEGG, KEGG Orthology, Gene Ontology,
Reactome, MSigDB, and GMT collections.

## Gene-set checklist

Confirm:

- every set has a meaningful name;
- every set maps to a list, not one text string;
- identifiers use the same system as `gene_id`;
- enough members match the measurement table;
- the set-size rule is recorded; and
- the collection source and release are recorded for real work.

[<- Previous: Read and prepare the matrix](08-prepare-expression.md) | [Home](index.md) | [Next: Run the one-call workflow ->](10-one-call-gage.md)
