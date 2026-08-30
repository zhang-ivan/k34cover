# Verification record

This record applies to version 0.4.3. The runtime generator implements the
complete spectrum for every integer order `v >= 3`.

## End-to-end generation

The release generator has been materialised and checked over the following
finite ranges:

- every order `3 <= v <= 500`, generated and certified by the constructor's
  full internal checker after the runtime-dependency refactor;
- every order `3 <= v <= 200`, independently rechecked with
  `k3k4cover_checker`;
- every order in the direct BIBD master family through `v = 500` in the
  preceding construction release, with the same construction logic retained.

For each generated order, the checker verifies:

1. every block has size 3 or 4 and contains valid, distinct vertices;
2. every edge of `K_v` is covered;
3. the excess multiplicity has the required size;
4. the numbers of `K3` and `K4` blocks equal the established optimum
   parameters for that order.

The fixed finite seeds are subjected to the same checks as designs returned by
the recursive construction families.

## Regression suite

Run:

```bash
python -m unittest discover -s tests -v
```

The permanent suite covers:

- a consecutive sweep through every order up to 100;
- all fixed finite optimum seeds;
- explicit and recursive Mills constructions;
- non-MacNeish transversal ingredients;
- Kirkman-system ingredients;
- 7-hole and Mills route selectors;
- command-line report generation, including complete block lists and a separate
  elapsed time for every requested order.

## Wide arithmetic route audit

Route selectors have also been tested without materialising the corresponding
quadratic-size designs:

- 7-hole/IPBD backend: every admissible parameter `u <= 100000`, corresponding
  to orders through `v = 300007`;
- Mills backend: every target order `n <= 1000000` in residues 7 and 10 modulo
  12.

These checks validate the deterministic routing logic over large finite ranges.
For orders beyond the materialised tests, the all-order claim rests on the
implemented recursive constructions together with their arithmetic existence
conditions and the explicitly stored finite optimum seeds.

## Command-line report checks

The CLI first imports the construction backends required by the requested
interval and records that one-time cost separately as ``initialization time``.
Only after this initialization boundary does it start the independent
high-resolution timer for each order.  Each per-order time therefore measures
construction plus built-in verification without charging Python module loading
to the first order in the interval.

The report also contains the complete normalised block list returned by the
constructor. This makes each report a directly inspectable certificate rather
than only a numerical summary.

## Standalone release artifact

Version 0.4.3 also ships as a self-contained `.pyz` application.  The active
package has no third-party runtime dependency, so the archive contains only
`k34cover` and the license.  Release smoke tests execute the archive from
outside the source tree, check its reported version, generate several
consecutive orders, and verify that the resulting report contains complete
designs, one-time initialization timing, and per-order generation timings.
GitHub Actions repeats this build-and-smoke-test step on Python 3.12.

## Performance note

The successful verification path counts distinct valid edge keys instead of
materialising the full edge set merely to prove that no edge is missing. The
command-line interface also avoids performing a second verification pass after
`cover_k3k4` has already certified a generated result.

## Runtime dependency audit

The active package no longer imports SymPy.  Primality testing, integer
factorisation, and finite-field irreducibility checks are provided by
`k34cover._number_theory` using exact deterministic algorithms.  During the
0.4.3 release audit, these helpers were cross-checked against SymPy over broad
finite test ranges before SymPy was removed from the runtime dependency list.
