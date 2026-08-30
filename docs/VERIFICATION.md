# Verification record

This record applies to version 0.4.0. The three-family implementation from
version 0.3.0 is retained, and the previously isolated order 17 is now supplied
by a verified optimum 29-block finite certificate. The runtime generator is
therefore complete for every order `v >= 3`.

## End-to-end generation

The release generator has been materialised and checked over the following
finite ranges:

- every order `3 <= v <= 500`, including `v = 17`, independently rechecked
  with `k3k4cover_checker`;
- every order in the direct BIBD master family through `v = 500`, independently
  rechecked.

For each generated order, the checker verifies:

1. every block has size 3 or 4 and contains valid, distinct vertices;
2. every edge of `K_v` is covered;
3. the excess multiplicity has the required size;
4. the numbers of `K3` and `K4` blocks equal the established optimum
   parameters for that order.

For order 17 specifically, the installed certificate has 29 blocks: 12
triangles and 17 quadruples. Its only repeated edges are `(1,2)` and `(1,3)`,
so its excess is exactly 2.

## Regression suite

Run:

```bash
python -m unittest discover -s tests -v
```

The permanent suite contains 12 tests covering:

- every order through 100, including 17;
- the finite exceptional coverings;
- the exact order-17 optimum profile and excess edges;
- explicit and recursive Mills constructions;
- non-MacNeish transversal ingredients;
- Kirkman-system ingredients;
- 7-hole and Mills route selectors;
- command-line generation across order 17.

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
conditions. Order 17 is independent of those recursions and is stored as an
explicit verified finite certificate.

## Performance note

The successful verification path counts distinct valid edge keys instead of
materialising the full edge set merely to prove that no edge is missing. The
command-line interface also avoids performing a second verification pass after
`cover_k3k4` has already certified a generated result.
