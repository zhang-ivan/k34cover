"""Small deterministic resolvable 4-BIBDs used by Brouwer's 7-hole recursion.

Only two finite ingredients are needed here: RBIBD(28,4,1) and
RBIBD(40,4,1).  Both are given by published cyclic/translation starters and
are generated algebraically; there is no search at run time.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Iterable, List, Sequence, Tuple

Block = Tuple[int, ...]
ParallelClass = Tuple[Block, ...]


def _verify_rbibd(v: int, classes: Sequence[Sequence[Sequence[int]]]) -> None:
    """Strong verification of a resolved 2-(v,4,1) design on 1..v."""
    expected_r = (v - 1) // 3
    if len(classes) != expected_r:
        raise AssertionError(f"RBIBD({v},4,1) has {len(classes)} classes, expected {expected_r}")
    mult: Counter[Tuple[int, int]] = Counter()
    seen_blocks = set()
    for cls in classes:
        flat = [x for B in cls for x in B]
        if sorted(flat) != list(range(1, v + 1)):
            raise AssertionError(f"RBIBD({v},4,1) class is not a partition")
        for raw in cls:
            B = tuple(sorted(raw))
            if len(B) != 4 or len(set(B)) != 4:
                raise AssertionError("invalid 4-block in RBIBD")
            if B in seen_blocks:
                raise AssertionError("repeated block in RBIBD resolution")
            seen_blocks.add(B)
            mult.update(combinations(B, 2))
    if len(mult) != v * (v - 1) // 2 or any(c != 1 for c in mult.values()):
        raise AssertionError(f"RBIBD({v},4,1) pair property failed")


def rbibd28() -> Tuple[ParallelClass, ...]:
    """Brouwer's translation RBIBD(28,4,1).

    Point set is Z_3^3 plus infinity.  Brouwer lists two full translation
    starters and one infinity starter.  A starter spread is obtained by
    developing only the third coordinate; its nine translates in the first
    two coordinates form the resolution.
    """
    INF = (3, 0, 0)  # sentinel outside Z_3^3

    def add(p, da=0, db=0, dc=0):
        if p == INF:
            return INF
        a, b, c = p
        return ((a + da) % 3, (b + db) % 3, (c + dc) % 3)

    A = ((0,1,1), (0,2,1), (1,0,2), (2,0,2))
    B = ((2,1,1), (1,2,1), (2,2,2), (1,1,2))
    C = (INF, (0,0,0), (0,0,1), (0,0,2))

    # Brouwer's starter parallel class: A and B developed in the third
    # coordinate, together with the infinity block C (which is invariant).
    starter: List[Tuple[tuple, ...]] = []
    for dc in range(3):
        starter.append(tuple(add(x, dc=dc) for x in A))
    for dc in range(3):
        starter.append(tuple(add(x, dc=dc) for x in B))
    starter.append(C)

    def label(p) -> int:
        if p == INF:
            return 28
        a, b, c = p
        return 1 + 9 * a + 3 * b + c

    classes: List[ParallelClass] = []
    for da in range(3):
        for db in range(3):
            cls = []
            for block in starter:
                cls.append(tuple(sorted(label(add(x, da=da, db=db)) for x in block)))
            classes.append(tuple(sorted(cls)))

    out = tuple(classes)
    _verify_rbibd(28, out)
    return out


def rbibd40() -> Tuple[ParallelClass, ...]:
    """Cyclically resolvable RBIBD(40,4,1) over Z_39 union {infinity}.

    Buratti--Zuanni give the starter parallel class below.  It is invariant
    under translation by 13, so its 13 translates by 0,...,12 are precisely
    the resolution classes.
    """
    INF = 39
    starter = (
        (27,12,31,34), (1,25,5,8), (14,38,18,21),
        (15,24,10,16), (28,37,23,29), (2,11,36,3),
        (30,9,7,19), (4,22,20,32), (17,35,33,6),
        (0,13,26,INF),
    )

    def shift(x: int, d: int) -> int:
        return INF if x == INF else (x + d) % 39

    classes: List[ParallelClass] = []
    for d in range(13):
        cls = [tuple(sorted((shift(x,d) + 1) for x in B)) for B in starter]
        # Here internal INF=39 becomes external point 40 after +1; finite
        # residues 0..38 become 1..39.
        classes.append(tuple(sorted(cls)))

    out = tuple(classes)
    _verify_rbibd(40, out)
    return out


__all__ = ["rbibd28", "rbibd40"]
