# Minimal K3 and K4 Covers of Complete Graphs

This project constructs and checks small covers of the complete graph \(K_v\) using triangles (K3) and 4‑cliques (K4). It focuses on the admissible orders
\[ v \equiv -1,0,1,2,3,4 \pmod{12} \]
where minimal‑excess covers are expected to exist.

The main script is **check_cover.py**, which builds covers for a range of values and produces a report showing the number of blocks used, whether any edges are covered twice, and whether the result matches the predicted behaviour. The output is written to a timestamped text file.

---

## Getting started

You can run everything directly in Python:

```bash
python check_cover.py
```

To test a different range of values, edit the call to `main(LB, UB)` at the bottom of the script.

Typical dependencies include:
- numpy
- sympy
- galois
- primefac

Install them using pip if necessary.

---

## How the construction works

The design behind this cover uses several building blocks:

- `bibd4.py` generates block designs of size 4 at specific orders,
- `gdd45_m4.py` assembles group‑divisible designs used inside the recursion,
- `transversal.py` produces transversal designs needed as ingredients,
- `pg2.py` builds finite projective planes that seed the transversal designs,
- `r_picker.py` selects suitable parameters for certain recursive steps.

All of these components fit together to supply enough structure to build the final K3 and K4 cover.

The script `k3k4cover.py` then translates these combinatorial designs into explicit triangle and 4‑clique blocks covering all edges of \(K_v\), with minimal excess. In the special cases \(v \equiv 2,11 \pmod{12}\), the theory predicts exactly two edges covered twice; the program reports those.

`assign_diagonal.py` exists as a simple helper for an auxiliary assignment step. It does not influence the cover generation itself and is not essential for normal use.

---

## What the output says

For each admissible \(v\), the report lists:
- any edges that appear twice (the “excess”),
- how many K3 and K4 blocks were used,
- a final consistency check (True/False).

If everything is correct, the check should be `True`. When \(v \equiv 2,11 \pmod{12}\), expect exactly two doubled edges.

---

## Structure overview

- **check_cover.py** — main driver and verifier
- **k3k4cover.py** — builds K3/K4 block lists from the design data
- **bibd4.py** — provides BIBD(v,4,1) constructions or seeds
- **gdd45_m4.py** — constructs \{4,5\}-GDDs with allowed group sizes
- **transversal.py** — transversal design constructors
- **pg2.py** — projective geometry needed for transversal designs
- **r_picker.py** — parameter helper for recursion
- **assign_diagonal.py** — optional bookkeeping/formatting helper

---

## Notes

- The cover is intended to be minimal in both size and excess.
- The designs are completely combinatorial rather than brute-force.
- The verifier is strict: if multiplicities do not match the expected pattern, the script stops with an error.



