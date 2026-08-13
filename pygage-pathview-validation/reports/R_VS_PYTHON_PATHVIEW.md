# R pathview versus Python Pathview Plus

## Verdict

The controlled `hsa04110` native-PNG half-and-half comparison passed.

- R pathview: 1.52.0
- Python Pathview Plus: 2.0.2
- Same frozen KGML and PNG: yes
- Same mapped controlled coordinates: 3
- Maximum mapped-value difference: 0.0
- First condition: Classical, left green
- Second condition: Basal, right red

Both implementations counted 316 green pixels on the left and 334 red pixels on the right inside the controlled CDKN2A node, with zero wrong-side green/red pixels.

Use native PNG for multi-state parity. R Graphviz supports multiple states; Python's graph/PDF implementation uses its first state only.

See `results/comparison/r_vs_python_half_half.png` and `results/comparison/comparison.json` for evidence.
