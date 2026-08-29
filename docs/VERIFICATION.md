# Verification record

This record applies to version 0.3.1. The mathematical construction code is the
same three-family implementation introduced in version 0.3.0; version 0.3.1
adds repository, documentation, metadata, and licensing cleanup together with
small interface-quality improvements.

Order 17 remains intentionally unsupported and is not used by any larger
construction.

## End-to-end generation

The refactored generator has been materialised and checked over the following
finite ranges:

- every order `3 <= v <= 250`, `v != 17`, independently rechecked with
  `k3k4cover_checker`;
- every order in the direct BIBD master family through `v = 500`, independently
  rechecked;
- every order `3 <= v <= 500`, `v != 17`, generated successfully and accepted
  by the complete internal verification performed by `cover_k3k4`.

For each generated order, the checker verifies:

1. every block has size 3 or 4 and contains valid, distinct vertices;
2. every edge of `K_v` is covered;
3. the excess multiplicity has the required size;
4. the numbers of `K3` and `K4` blocks equal the established optimum
   parameters for that supported order.

## Regression suite

Run:

```bash
python -m unittest discover -s tests -v
```

The permanent suite contains 12 tests covering:

- all residue branches through order 100, excluding 17;
- the finite exceptional coverings;
- explicit and recursive Mills constructions;
- non-MacNeish transversal ingredients;
- Kirkman-system ingredients;
- 7-hole and Mills route selectors;
- command-line behaviour at the unsupported order 17.

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
conditions.

## Performance note

The successful verification path counts distinct valid edge keys instead of
materialising the full edge set merely to prove that no edge is missing. The
command-line interface also avoids performing a second verification pass after
`cover_k3k4` has already certified a generated result.
