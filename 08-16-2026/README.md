# August 16, 2026: quantum methods for MS/MS

This folder summarizes the research direction I developed from the supplied
quantum-computing and mass-spectrometry notes. The main focus is candidate
spectrum retrieval: given an unknown MS/MS spectrum, decide which library
spectrum or molecular candidate best explains it.

This is an exploratory research plan, not a report of a finished algorithm or
a new benchmark result.

## The problem I am trying to solve

An MS/MS experiment produces fragment peaks. The measured mass and intensity
are not perfectly exact, and some peaks can be missing or noisy. The goal is to
compare an unknown spectrum with candidate spectra while keeping the chemistry
of the experiment in the comparison.

I chose candidate-spectrum retrieval as the first problem because it lets me
test the spectral representation before attempting the much harder problem of
de novo structure prediction.

## What happens before the quantum step

The first part of the workflow is classical signal processing:

1. Start with the observed fragment masses and intensities.
2. Represent each peak as a small uncertainty distribution instead of an
   infinitely exact stick.
3. Use a log-mass coordinate so that approximately constant ppm errors are
   treated more consistently.
4. Apply a continuous wavelet transform to describe the spectrum at several
   scales.
5. Summarize the wavelet information as a fixed feature vector with values
   between 0 and 1.

The wavelet step is meant to retain broader peak patterns, not just exact
peak-to-peak matches. This whole section can be implemented and tested with
ordinary numerical methods before any quantum circuit is introduced.

## Related methods I reviewed

The notes connect this idea to existing work on wavelet-based MS processing,
dynamic wavelet scales, soft peak and neutral-loss kernels, and sparse peak
interactions. These are useful classical baselines and help separate a real
contribution from a rebranding of an existing similarity method. Public
centroid-spectrum collections and controlled candidate splits are possible
later data sources, but no new dataset result is claimed in this entry.

## Where the quantum representation begins

Each normalized feature can be mapped to a rotation angle and encoded in a
qubit. The first version treats the features independently. I noted an
important limitation: the resulting fidelity kernel has an exact classical
product form, so independent qubit encoding alone does not demonstrate a
quantum advantage.

The part I want to investigate is the relationship between features. A sparse
relationship graph could include:

- fragment co-occurrence;
- chemically meaningful neutral-loss relationships;
- neighboring wavelet scales; and
- local mass relationships.

The graph can then control spectrum-dependent two-feature interactions. The
resulting state is intended as a mathematical representation of related
evidence in a spectrum. It is not a claim that molecular fragments are
physically entangled.

## Chemistry stays in the score

The representation should not become a generic vector-similarity exercise.
Candidate filtering or scoring should use precursor neutral mass, charge,
adduct, ionization mode, isotope compatibility, fragment agreement, and
neutral-loss evidence. A provisional retrieval score can combine the
interaction-aware kernel with neutral-loss, isotope, and fragment scores, but
the exact weights still need to be defined and tested.

The chemistry rules should be evaluated first and documented clearly. A
candidate should not rank highly only because it happens to share a few peaks.

## Why Grover appeared in the notes

My earlier Grover notebook searched a secret four-bit code by comparing a
classical brute-force search with amplitude amplification. The useful
connection is the general search pattern:

`unknown answer + candidate space + rule for evaluating candidates`

For MS/MS, the evaluation rule would need to ask whether a candidate is
chemically compatible and explains the observed spectrum. Grover is therefore
an inspiration for the search structure, not a decision that Grover is the
final algorithm. A quantum walk, QAOA, or a classical graph or Bayesian method
may fit a particular formulation better.

## DIA and alignment direction

The same reasoning may apply later to DIA, where one acquisition window can
contain fragments from multiple precursors. Retention-time alignment, wave
alignment, and uncertainty could help decide which precursor best explains a
fragment. I have not assumed that DIA is automatically a quantum problem, and
I have not filled in mathematical details for alignment methods that I have
not yet inspected.

## Next tests

The next useful test is a small, reproducible retrieval benchmark:

1. make a controlled synthetic set with mass shifts, intensity changes,
   missing peaks, and noise;
2. compare ordinary peak, wavelet, and soft-peak classical baselines;
3. add the relationship graph as an ablation, so its contribution is visible;
4. enforce the same chemistry filters for every method; and
5. test public spectra only after the synthetic behavior is understood.

For every proposed quantum method, I need to state what the state, oracle or
cost function, uncertainty model, classical comparison, hardware setting, and
failure test mean in MS terms.

## Current takeaway

The strongest version of the idea is chemistry-first candidate retrieval with
an uncertainty-aware, wavelet-based spectrum representation and an optional
interaction-aware quantum or quantum-inspired layer. The first question is not
whether a quantum method sounds faster. It is whether the feature relationships
add measurable retrieval information beyond a well-designed classical model.

## Request versus attached material

The request for this folder was to summarize the work for August 16. The
attached PDFs and pasted notes supplied the scientific background and cautions
used in that summary: keep chemistry central, compare against strong classical
baselines, treat Grover as exploratory, and avoid claiming a finished quantum
advantage. They were treated as research notes, not as instructions to run
software or as evidence that new experiments had already been completed.
