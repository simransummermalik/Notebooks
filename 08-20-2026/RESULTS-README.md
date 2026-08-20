# August 20 results — simple explanation

## What I tested

I used real MS/MS spectra from MassSpecGym. The notebook used 20 query spectra
and 100 possible reference spectra. Each query had a matching spectrum from
the same molecule, so the correct answer was known.

The question was simple:

> Which method puts the matching molecule closest to rank 1?

## The results

| Method | Top-1 result | Plain-English meaning |
|---|---:|---|
| Binned cosine | 100% | Found the correct molecule first for all 20 queries. |
| Soft peak | 100% | Also found the correct molecule first every time. |
| Tolerance peak | 95% | Found the correct molecule first for 19 of 20 queries. |
| Wavelet cosine | 75% | Found the correct molecule first for 15 of 20 queries. |
| PennyLane independent | 50% | Found the correct molecule first for 10 of 20 queries. |
| PennyLane `ZZ` interaction | 50% | Also found the correct molecule first for 10 of 20 queries. |

## What this means

The ordinary classical methods performed best in this first test. The
PennyLane interaction circuit did not improve the result over the simpler
PennyLane circuit.

That does not mean the quantum idea is impossible. It means the current
features and interaction graph did not add useful information in this test.

The wavelet result was lower because the notebook compressed the wavelet
information heavily. It kept average and maximum values for each scale, but it
did not keep enough information about where the peaks occurred in the mass
range.

## Important limits of this test

- There were only 20 queries and 100 candidates.
- The test paired two spectra from the same molecule, so it measured stability,
  not performance on completely unseen molecules.
- The candidate filter did not reduce the library below 100 candidates in the
  saved run.
- This was a PennyLane statevector simulation, not a speed test on a quantum
  computer.
- The results do not show a quantum advantage.

## What I should do next

1. Keep the classical methods as the baseline.
2. Improve the wavelet features by keeping mass-location information.
3. Test several interaction strengths and graph choices.
4. Compare the independent and `ZZ` circuits using exactly the same features.
5. Run the larger official MassSpecGym retrieval split after the small test is
   working.

## conclusion

The first real-data test worked, but the classical methods were stronger and
the current PennyLane interaction did not improve retrieval, so the feature
representation needs more testing before making a larger claim.

## Saved evidence

- [`method_summary.csv`](colab_outputs/method_summary.csv) — summary scores;
- [`query_ranks.csv`](colab_outputs/query_ranks.csv) — rank for every query and method; and
- [`method_summary.png`](colab_outputs/method_summary.png) — bar chart of the results.
