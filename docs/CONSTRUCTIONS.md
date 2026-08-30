# Construction architecture

This document records the construction routes used by the runtime generator.
The implementation is deterministic and contains no exact-cover or
optimisation search.

## Three master families

### 1. BIBD(4) truncation

Target residues:

```text
v mod 12 in {0, 1, 2, 3, 4, 11}.
```

Choose `s in {0,1,2}` so that `v+s` is congruent to 1 or 4 modulo 12 and
construct a `2-(v+s,4,1)` design.

- `s = 0` (`v mod 12 in {1,4}`): retain the BIBD unchanged.
- `s = 1` (`v mod 12 in {0,3}`): delete one point. Blocks through that point
  become exactly the required triangles; all other blocks remain quadruples.
- `s = 2` (`v mod 12 in {2,11}`): delete two points. Their unique common
  source block leaves one 2-set. Discard that remnant and add one triangle
  through the surviving pair. The added triangle covers the missing pair and
  creates exactly two repeated edge occurrences.

This single routine replaces the older group-reconstruction and `v+1 -> v`
recursive front-end routes.

### 2. Seven-hole PBD truncation and filling

Target residues:

```text
v mod 12 in {5, 7, 8, 10}.
```

The backend constructs a `PBD(n,{4,7*},1)` with one distinguished 7-point
hole.

- `v mod 12 in {7,10}`: fill the 7-hole with the Fano plane.
- `v mod 12 in {5,8}`: construct the hole design at order `v+2`, delete two
  points of the distinguished hole, and fill the remaining 5-set with the
  fixed optimum order-5 covering.

Orders 5, 7, 20, and 22 are ordinary instances of this family rather than
separate top-level constructions.

### 3. Mills truncation

Target residues:

```text
v mod 12 in {6, 9}.
```

Construct the relevant optimum quadruple covering on `v+1` points using the
Mills recursion. Its distinguished repeated pair occurs four times. Deleting
one endpoint converts incident quadruples to triangles and removes the excess,
leaving the required exact `{K3,K4}` decomposition of order `v`.

This route is mathematically distinct from the BIBD and 7-hole families and is
therefore retained as a separate master construction.

## Finite exceptions

The top-level generator stores only the finite optimum constructions that are
not instances of the three master families:

```text
6, 8, 9, 10, 17, 18, 19.
```

The last case, order 17, is a 29-block certificate with 12 triangles and 17
quadruples and excess 2. It is stored directly because the general residue-5
route does not specialise to that order. See [`ORDER17.md`](ORDER17.md).

## Shared infrastructure

The front-end simplification does not make the underlying BIBD, GDD, PBD, or
transversal modules redundant. The recursive families share these ingredients.
In particular, the BIBD(4) machinery is used directly by the first master
family and indirectly by later construction modules.

Implementation details relevant to performance and maintainability include:

- bounded caches for BIBD and 7-hole designs;
- a common truncation-and-relabel helper for mechanical point deletion;
- shared primitive PBD(22) and PBD(46) ingredients;
- table-based dispatch for fixed BIBD seeds;
- route selection before materialising exceptional transversal designs;
- inactive historical helpers isolated under `k34cover.legacy`.

## Verification boundary

The public `cover_k3k4(v)` function verifies a constructed cover before it is
returned. This check includes coverage, excess size, and the expected numbers
of triangle and quadruple blocks. The separate public checker remains available
for independent validation of externally supplied block lists.
