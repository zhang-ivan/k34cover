# k34cover

`k34cover` constructs optimum minimum-excess coverings of the complete graph
\(K_v\) by triangles \(K_3\) and 4-cliques \(K_4\), for every integer
`v >= 3`.

The implementation is deterministic and design-theoretic. Runtime generation
uses explicit finite designs together with recursive BIBD, GDD, PBD,
transversal-design, Kirkman-system, and Mills constructions. It does **not**
use ILP, SAT, dancing links, backtracking, or other combinatorial search.

## Status

Version **0.4.0** covers the complete spectrum: every order `v >= 3` is
implemented and verified against the established optimum parameters. The last
finite case, `v = 17`, is supplied by an explicit optimum 29-block certificate
with 12 triangles, 17 quadruples, and excess 2.

The twelve residue classes modulo 12 are handled by three construction
families, with a small set of finite exceptions:

| `v mod 12` | construction family |
| --- | --- |
| `0, 1, 2, 3, 4, 11` | direct truncation of a `2-(v+s,4,1)` design, `s in {0,1,2}` |
| `5, 7, 8, 10` | filling/truncation of a `PBD(v+s,{4,7*},1)`, `s in {0,2}` |
| `6, 9` | truncation of an optimum Mills covering by quadruples |

The separately stored finite optimum coverings are
`v = 6, 8, 9, 10, 17, 18, 19`. See
[`docs/CONSTRUCTIONS.md`](docs/CONSTRUCTIONS.md) for the construction map and
[`docs/ORDER17.md`](docs/ORDER17.md) for the final order-17 certificate.

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
working directory. Every order in the requested range is generated.

## Python API

```python
from k34cover.cover import cover_k3k4
from k34cover.verify import k3k4cover_checker

result = cover_k3k4(17)

print(result.v)
print(result.n_k3, result.n_k4)   # 12, 17
print(result.xi)                  # [(1, 2), (1, 3)]
print(len(result.blocks))         # 29

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

Release verification includes:

- all 12 permanent regression tests;
- end-to-end generation and checking for every `3 <= v <= 500`, including 17;
- an independent sweep of the complete BIBD-truncation family through `v=500`;
- wide arithmetic route audits for the 7-hole and Mills recursive selectors.

Details and scope are recorded in [`docs/VERIFICATION.md`](docs/VERIFICATION.md).
Continuous integration runs the regression suite on supported Python versions.

## Repository structure

```text
k34cover/
├── .github/workflows/       # GitHub Actions regression tests
├── docs/                    # construction and verification notes
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
- `designs/small.py`: fixed finite optimum coverings and PBD ingredients.

## Mathematical scope

The software implements the design-theoretic construction framework for the
`{K3,K4}` lexicographic covering problem: first minimise repeated edge
occurrences, then minimise the number of blocks among coverings with minimum
excess. It produces explicit certificates, not only numerical optimum values.

For `v = 17`, the arithmetic 28-block candidate would have profile
`(excess, K3, K4) = (2, 10, 18)`, but that profile is impossible. The installed
29-block certificate has profile `(2, 12, 17)` and therefore attains the exact
secondary optimum. See [`docs/ORDER17.md`](docs/ORDER17.md).

## License

The software is distributed under the **K34Cover Non-Commercial Limited
Modification License v1.0**. In brief, non-commercial use and verbatim
redistribution are permitted, while public redistribution of modified versions
and commercial use require prior written permission from the copyright holder.

This is a custom source-available license, not an OSI-approved open-source
license. The complete terms in [`LICENSE`](LICENSE) control.
