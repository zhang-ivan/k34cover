# k34cover

`k34cover` constructs optimum minimum-excess coverings of the complete graph
\(K_v\) by triangles \(K_3\) and 4-cliques \(K_4\), for every integer
`v >= 3`.

The implementation is deterministic and design-theoretic. Runtime generation
uses explicit finite designs together with recursive BIBD, GDD, PBD,
transversal-design, Kirkman-system, and Mills constructions. It does **not**
use ILP, SAT, dancing links, backtracking, or other combinatorial search.

## Status

Version **0.4.3** implements and verifies the complete spectrum for every
integer `v >= 3`.

The twelve residue classes modulo 12 are handled by three construction
families, together with a small set of fixed finite optimum seeds:

| `v mod 12` | construction family |
| --- | --- |
| `0, 1, 2, 3, 4, 11` | direct truncation of a `2-(v+s,4,1)` design, `s in {0,1,2}` |
| `5, 7, 8, 10` | filling/truncation of a `PBD(v+s,{4,7*},1)`, `s in {0,2}` |
| `6, 9` | truncation of an optimum Mills covering by quadruples |

The fixed finite optimum seeds are `v = 6, 8, 9, 10, 17, 18, 19`. They are
handled uniformly by the finite-seed dispatcher. See
[`docs/CONSTRUCTIONS.md`](docs/CONSTRUCTIONS.md) for the construction map.

## Requirements

- Python 3.9 or later

The active generator has **no third-party runtime dependencies**.  The finite-field
number theory required by the transversal-design backend is implemented locally
with exact deterministic routines.  A legacy projective-plane helper additionally
requires `galois`; install it through the optional extra if needed.

## Running k34cover

### Standalone executable (recommended for ordinary use)

GitHub releases provide `k34cover-0.4.3.pyz`, a self-contained Python
executable containing the active package. It does
not install anything into the system Python and therefore is unaffected by
Ubuntu/Debian PEP 668 `externally-managed-environment` restrictions.

On Linux or macOS:

```bash
chmod +x k34cover-0.4.3.pyz
./k34cover-0.4.3.pyz --lb 7 --ub 60 --output report.txt
```

It can also be launched without changing its executable bit:

```bash
python3 k34cover-0.4.3.pyz --lb 7 --ub 60 --output report.txt
```

The standalone file requires only a local Python 3.9+ interpreter. No `pip`,
virtual environment, or administrator access is required.

### Install as a command with pipx

For users who prefer a normal `k34cover` command, `pipx` is the recommended
installer on current Ubuntu and Debian systems because it creates and manages
an isolated environment automatically:

```bash
sudo apt install pipx
pipx ensurepath
pipx install .
```

After reopening the terminal if requested by `pipx`, run:

```bash
k34cover --lb 7 --ub 60 --output report.txt
```

### Development installation

Do not run `pip install -e .` directly against the system Python on a
PEP 668-managed distribution. Create a project virtual environment instead:

```bash
git clone https://github.com/zhang-ivan/k34cover.git
cd k34cover
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

If `python3 -m venv` is unavailable on Ubuntu/Debian, install the distribution
package first:

```bash
sudo apt install python3-venv
```

Optional legacy projective-plane support, from inside the virtual environment:

```bash
python -m pip install -e '.[legacy-pg2]'
```

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md) for platform notes and an
explanation of the PEP 668 message.

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
working directory. Every requested order is generated independently.

The report first records a one-time **initialization time** for loading the
construction backends required by the requested interval.  This cost is kept
separate so that the first requested order does not inherit Python import time.

For each order, the report then records:

- elapsed generation time for that order, including the built-in verification
  but excluding one-time backend initialization;
- the excess multiset;
- the numbers of triangles, quadruples, and total blocks;
- the **complete block list** of the generated design;
- the verification result.

The terminal prints a concise progress line and the elapsed time for each order.
For example, a request with `--lb 30 --ub 33` reports three separate timings,
one each for orders 30, 31, and 32.

## Python API

```python
from k34cover.cover import cover_k3k4
from k34cover.verify import k3k4cover_checker

result = cover_k3k4(22)

print(result.v)
print(result.n_k3, result.n_k4)   # 7, 35
print(result.xi)                  # []
print(len(result.blocks))         # 42
print(result.blocks)              # complete design

# Optional independent re-check.
assert k3k4cover_checker(result.v, result.blocks)
```

`cover_k3k4(v)` verifies the complete construction before returning. The
returned `CoverResult` contains:

- `v`: order of the complete graph;
- `blocks`: sorted 3- and 4-subsets forming the complete design;
- `xi`: repeated edge occurrences (the excess multiset represented as a list);
- `n_k3`: number of triangle blocks;
- `n_k4`: number of 4-clique blocks.

## Verification

Run the permanent regression suite with:

```bash
python -m unittest discover -s tests -v
```

Release verification includes:

- the permanent regression suite;
- end-to-end generation and checking for every `3 <= v <= 500`;
- an independent sweep of the complete BIBD-truncation family through `v=500`;
- wide arithmetic route audits for the 7-hole and Mills recursive selectors;
- command-line checks that every requested order has its own timing and complete
  block list in the report.

Details and scope are recorded in [`docs/VERIFICATION.md`](docs/VERIFICATION.md).
Continuous integration runs the regression suite on supported Python versions.

## Repository structure

```text
k34cover/
├── .github/workflows/       # GitHub Actions regression tests
├── docs/                    # installation, construction, and verification notes
├── k34cover/
│   ├── cover.py             # public three-family dispatcher
│   ├── verify.py            # edge multiplicity and optimum-parameter checks
│   ├── cli.py               # command-line interface and report writer
│   ├── designs/             # active combinatorial construction modules
│   └── legacy/              # inactive compatibility helpers
├── scripts/                 # reproducible release-build helpers
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

## License

The software is distributed under the **K34Cover Non-Commercial Limited
Modification License v1.0**. In brief, non-commercial use and verbatim
redistribution are permitted, while public redistribution of modified versions
and commercial use require prior written permission from the copyright holder.

This is a custom source-available license, not an OSI-approved open-source
license. The complete terms in [`LICENSE`](LICENSE) control.
