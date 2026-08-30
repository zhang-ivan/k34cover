# Order 17

Order `v = 17` is fully solved and implemented in version 0.4.0.

The minimum excess is

```text
xi = 2.
```

With excess fixed at 2, the theoretical edge-count lower bound first permits
28 blocks, corresponding to

```text
K3 blocks = 10
K4 blocks = 18
```

because `3*10 + 6*18 = C(17,2) + 2 = 138`. A separate finite structural
argument excludes this 28-block profile. Therefore every minimum-excess
covering of `K_17` has at least 29 blocks.

The software stores the following matching 29-block certificate:

```text
(1,2,4,13)     (1,2,14,16)    (1,3,5,15)
(1,3,7,11)     (1,6,8,9)      (1,10,12,17)
(2,3,9,17)     (4,5,8,16)     (4,6,11,12)
(4,7,9,10)     (5,6,13,17)    (5,7,12,14)
(6,10,14,15)   (7,8,13,15)    (8,11,14,17)
(9,12,15,16)   (10,11,13,16)

(2,5,10)       (2,6,7)        (2,8,12)
(2,11,15)      (3,4,14)       (3,6,16)
(3,8,10)       (3,12,13)      (4,15,17)
(5,9,11)       (7,16,17)      (9,13,14)
```

The first 17 blocks are quadruples and the final 12 are triangles. Direct edge
multiplicity verification gives no uncovered pair and exactly two repeated
edges:

```text
(1,2), (1,3).
```

Hence the exact optimum parameters are

```text
(excess, K3 blocks, K4 blocks, total blocks) = (2, 12, 17, 29).
```

The construction is exposed through the normal API:

```python
from k34cover.cover import cover_k3k4

r = cover_k3k4(17)
assert len(r.blocks) == 29
assert r.n_k3 == 12
assert r.n_k4 == 17
assert r.xi == [(1, 2), (1, 3)]
```

No larger recursive construction depends on this finite seed; it closes the
only previously missing order and makes the runtime generator complete for all
`v >= 3`.
