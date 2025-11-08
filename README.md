# Minimal K3 and K4 Covers of Complete Graphs with Minimum Excess

This program constructs and verifies optimal covers of the complete graph K_v by 3-cliques (K3) and 4-cliques (K4).  
It works for all admissible orders

    v ≡ −1, 0, 1, 2, 3, 4 (mod 12)

where minimal or near-minimal covers are known to exist.  
The code outputs explicit lists of 3- and 4-vertex blocks covering every edge of K_v with the smallest possible excess.

---

## Installation

Clone the repository and install it locally:

```bash
git clone https://github.com/zhang-ivan/k34cover.git
cd k34cover
pip install -e .
```

Requirements:
- Python 3.9 or newer  
- numpy, sympy, galois, primefac

All dependencies install automatically.

---

## How to run

You can run the generator either as a command-line program or as a module.

### 1. Command line

```bash
k34cover --lb 7 --ub 60 --output my_report.txt
```

### 2. Module form

```bash
python -m k34cover.cli --lb 7 --ub 60 --output my_report.txt
```

If you omit the `--output` argument, a timestamped file like  
`output_2025-11-08_23-55-10.txt` is created automatically.

---

## Output format

For each admissible v, the report lists for example:

```
------------
order = 52
excess for K-52:
[]
number of triples: 221
number of quadruples: 0
check result for K-52:
True
```

- **excess** – list of edges covered twice (empty if the cover is exact)
- **number of triples / quadruples** – counts of K3 and K4 blocks
- **check result** – confirmation that the multiplicity matrix is correct

---

## Background

The construction is based on explicit combinatorial designs.

- `bibd4.py` – builds BIBD(v,4,1) designs when they exist  
- `gdd45_m4.py` – mixed group-divisible designs with block sizes 4 and 5  
- `transversal.py` – transversal designs used in the recursion  
- `pg2.py` – finite projective plane PG(2,q) generator  
- `cover.py` – main routine constructing the K3/K4 cover  
- `verify.py` – edge-multiplicity checks  
- `utils/assign_diagonal.py` – optional helper for diagonal blocks assignment

All constructions are algebraic; no brute-force search is used.

---

## Project layout

```
k34cover/
├── __init__.py
├── cli.py          # command-line interface
├── cover.py        # K3 and K4 cover builder
├── verify.py       # checking covers
├── designs/
│   ├── bibd4.py
│   ├── gdd45_m4.py
│   ├── pg2.py
│   └── transversal.py
└── utils/
    └── assign_diagonal.py
```

After installation, the `k34cover` command and the module `k34cover.cli` are both available.

---

## Example (interactive use)

```python
from k34cover.cover import cover_k3k4

res = cover_k3k4(52)
print(res.v, res.n_k3, res.n_k4)
print(res.xi)        # doubled edges, if any
print(res.blocks[:5])
```

---

## Notes

- Each block is stored as a tuple of sorted vertices.
- Verification ensures that each edge appears exactly once, except two edges when v ≡ 2 or 11 (mod 12).
- Runtime is moderate even for large v since the method is purely combinatorial.

---

## License

This project is distributed under the Creative Commons Attribution–NonCommercial 4.0 
International License (CC BY-NC 4.0).  
See the [LICENSE](LICENSE) file for the full text.

