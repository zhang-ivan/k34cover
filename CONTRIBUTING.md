# Contributing

Contributions that improve correctness, reproducibility, documentation, or the
design-theoretic implementation are welcome for review.

## Before making a substantial change

For changes to construction logic, recursive routes, finite seeds, or public
APIs, open an issue first and describe:

- the mathematical result or software problem being addressed;
- the proposed construction or implementation change;
- any new literature or finite certificate on which the change depends;
- how the change will be independently verified.

Small documentation fixes and narrowly scoped bug fixes may be submitted
directly.

## Development setup

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

The active package supports Python 3.9 and later.

## Coding expectations

- Keep runtime generation deterministic and design-theoretic. Do not introduce
  search-based construction as a hidden fallback.
- Use explicit assertions or exceptions for violated construction invariants;
  do not silently continue after a failed design condition.
- Keep theorem-level construction routes separate from mechanical helpers such
  as relabelling and truncation.
- Add type annotations and concise docstrings to new public or nontrivial
  functions.
- Avoid debug output in library code. Diagnostic output should be opt-in.
- Preserve deterministic ordering where practical so generated certificates
  are reproducible.

## Tests

Every change to construction code should include or extend a regression test.
At minimum, run:

```bash
python -m unittest discover -s tests -v
python -m compileall -q k34cover
```

For a new finite seed, verify the complete block list independently before
adding it to the runtime package.

## Documentation and provenance

When a construction comes from the literature, record enough provenance in the
module docstring or accompanying documentation to identify the result being
implemented. Do not replace a cited design-theoretic argument with an uncited
search-generated object unless the project explicitly decides to do so.

## License of contributions

By submitting a contribution for inclusion in this repository, you agree that
the accepted contribution may be distributed as part of `k34cover` under the
license in [`LICENSE`](LICENSE). If you cannot agree to that, do not submit the
contribution without first arranging separate written terms with the project
maintainer.
