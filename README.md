# k34cover

`k34cover` constructs minimum-excess coverings of the complete graph \(K_v\)
by triangles \(K_3\) and 4-cliques \(K_4\).

The implementation is deterministic and design-theoretic. Runtime generation
uses explicit finite designs together with recursive BIBD, GDD, PBD,
transversal-design, Kirkman-system, and Mills constructions. It does **not**
use ILP, SAT, dancing links, backtracking, or other combinatorial search.

## Current status

Version **0.3.1** implements every order `v >= 3` except the isolated finite
case `v = 17`, which is intentionally unsupported while its optimum block
count is treated separately. No recursive construction depends on order 17.

The twelve residue classes modulo 12 are handled by three construction
families:

| `v mod 12` | construction family |
| --- | --- |
| `0, 1, 2, 3, 4, 11` | direct truncation of a `2-(v+s,4,1)` design, `s in {0,1,2}` |
| `5, 7, 8, 10` | filling/truncation of a `PBD(v+s,{4,7*},1)`, `s in {0,2}` |
| `6, 9` | truncation of an optimum Mills covering by quadruples |

The separately stored finite constructions are `v = 6, 8, 9, 10, 18, 19`.
See [`docs/CONSTRUCTIONS.md`](docs/CONSTRUCTIONS.md) for the construction map
and [`docs/ORDER17.md`](docs/ORDER17.md) for the status of order 17.

## Requirements

- Python 3.9 or later
- `sympy`

The active generator has no other runtime dependency. A legacy projective-plane
helper additionally requires `galois`; install it through the optional extra if
needed.

## Installation

For local development:

```bash
git clone https://github.com/zhang-ivan/k34cover.git
cd k34cover
python -m pip install -e .
```

Optional legacy projective-plane support:

```bash
python -m pip install -e '.[legacy-pg2]'
```

## Command-line interface

Generate all orders in the half-open interval `[lb, ub)`:

```bash
k34cover --lb 7 --ub 60 --output report.txt
```

The equivalent module invocation is:

```bash
python -m k34cover.cli --lb 7 --ub 60 --output report.txt
```

If `--output` is omitted, a timestamped report is created in the current
working directory. The unsupported order 17 is reported as `NOT IMPLEMENTED`
and does not terminate a range run.

## Python API

```python
from k34cover.cover import cover_k3k4
from k34cover.verify import k3k4cover_checker

result = cover_k3k4(90)

print(result.v)
print(result.n_k3, result.n_k4)
print(result.xi)
print(result.blocks[:5])

# Optional independent re-check.
assert k3k4cover_checker(result.v, result.blocks)
```

`cover_k3k4(v)` verifies the complete construction before returning. The
returned `CoverResult` contains:

- `v`: order of the complete graph;
- `blocks`: sorted 3- and 4-subsets;
- `xi`: repeated edge occurrences (the excess multiset represented as a list);
- `n_k3`: number of triangle blocks;
- `n_k4`: number of 4-clique blocks.

## Verification

Run the permanent regression suite with:

```bash
python -m unittest discover -s tests -v
```

The release verification includes:

- all 12 permanent regression tests;
- end-to-end generation and checking for every `3 <= v <= 500`, except 17;
- an independent sweep of the complete BIBD-truncation family through `v=500`;
- wide arithmetic route audits for the 7-hole and Mills recursive selectors.

Details and scope are recorded in [`docs/VERIFICATION.md`](docs/VERIFICATION.md).
Continuous integration runs the regression suite on supported Python versions.

## Repository structure

```text
k34cover/
├── .github/workflows/       # GitHub Actions regression tests
├── docs/                    # construction, verification, and order-17 notes
├── k34cover/
│   ├── cover.py             # public three-family dispatcher
│   ├── verify.py            # edge multiplicity and optimum-parameter checks
│   ├── cli.py               # command-line interface
│   ├── designs/             # active combinatorial construction modules
│   └── legacy/              # inactive compatibility helpers
├── tests/                   # regression tests
├── CHANGELOG.md
├── CITATION.cff
├── CONTRIBUTING.md
├── LICENSE
└── pyproject.toml
```

Important design modules are:

- `designs/bibd4.py`: `2-(v,4,1)` constructions and finite BIBD seeds;
- `designs/gdd45_m4.py`: mixed `{4,5}` group-divisible designs;
- `designs/transversal.py`: transversal-design ingredients;
- `designs/hole7.py`: constructive 7-hole PBD/IPBD backend;
- `designs/kirkman.py`: resolvable Steiner triple systems;
- `designs/mills.py`: optimum quadruple coverings and Mills recursions;
- `designs/resolvable.py`: finite resolvable `2-(v,4,1)` ingredients;
- `designs/small.py`: fixed finite covering and PBD ingredients.

## Mathematical scope

The software implements the design-theoretic construction framework used for
the `{K3,K4}` minimum-excess covering problem. It is intended to produce
explicit certificates rather than merely numerical optimum values. The
construction code therefore mirrors the recursive design ingredients rather
than replacing them by search.

## Citation

If the software materially contributes to academic work, please cite it. The
repository includes machine-readable metadata in [`CITATION.cff`](CITATION.cff)
and `.zenodo.json`.

## License

This project is distributed under the **K34Cover Non-Commercial Limited
Modification License v1.0**, a custom source-available license.

In brief, non-commercial use and redistribution of unmodified copies are
permitted. Local modifications are permitted for private or internal
non-commercial work, but modified versions may not be publicly redistributed
without prior written permission from the copyright holder. Commercial use
also requires prior written permission.

The custom license is **not** an OSI-approved open-source license. See
[`LICENSE`](LICENSE) for the complete terms; the full license text controls if
this summary differs from it.
