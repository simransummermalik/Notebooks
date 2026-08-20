# August 20, 2026: real MS/MS retrieval and PennyLane test

Open `08-20-2026-msms-pennylane-colab.ipynb` in Google Colab. The notebook
downloads the public MassSpecGym v1.5 spectrum table, keeps a small working
subset, and compares ordinary spectral matching with a small PennyLane
feature-interaction circuit.

## What the notebook tests

The notebook is a first real-data smoke test. It:

1. loads measured MS/MS peak lists and metadata;
2. makes paired query/reference spectra from the same molecule;
3. applies precursor/adduct filtering;
4. compares cosine, tolerance-based, soft-peak, and wavelet features; and
5. compares an independent PennyLane encoding with a small `ZZ` interaction
   graph.

The paired setup tests whether a representation is stable when spectra from
the same molecule differ. It is not yet the final MassSpecGym leaderboard
benchmark. The notebook states this limitation so the result is not
overinterpreted.

## Colab use

1. Upload the `.ipynb` file to Google Colab.
2. Run the installation cell first.
3. Start with the default 20,000-row read and 100-candidate library.
4. Increase the settings only after the small run completes.
5. Download or save the CSV and PNG files written to
   `/content/aug20_msms_outputs/`.

The dataset is downloaded from the public MassSpecGym repository on Hugging
Face. The notebook does not modify the source dataset or make any claim about
quantum speedup.
