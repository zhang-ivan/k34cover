"""Fixed small design ingredients for optimum K3/K4 coverings.

These are finite certificates used as endpoints of the recursive construction
machinery.  They are stored explicitly or generated from tiny classical
systems; no search is used at runtime.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable, List, Sequence, Tuple

Block = Tuple[int, ...]


def _norm(blocks: Iterable[Sequence[int]]) -> List[Block]:
    return sorted((tuple(sorted(map(int, B))) for B in blocks), key=lambda B:(len(B),B))


def relabel(blocks: Iterable[Sequence[int]], source_points: Sequence[int], target_points: Sequence[int]) -> List[Block]:
    if len(source_points) != len(target_points):
        raise ValueError("source and target point lists have different lengths")
    mp = {int(x):int(y) for x,y in zip(source_points,target_points)}
    if len(mp) != len(source_points):
        raise ValueError("source point list contains duplicates")
    return _norm(tuple(mp[int(x)] for x in B) for B in blocks)


def fano7(points: Sequence[int] | None = None) -> List[Block]:
    base = [
        (1,2,3),(1,4,5),(1,6,7),
        (2,4,6),(2,5,7),(3,4,7),(3,5,6),
    ]
    if points is None:
        return _norm(base)
    if len(points) != 7:
        raise ValueError("Fano relabelling needs seven target points")
    return relabel(base, tuple(range(1,8)), tuple(points))


def sts9() -> List[Block]:
    from . import kirkman
    return _norm(B for cls in kirkman.kirkman_triple_system(9) for B in cls)


def cover5() -> List[Block]:
    return _norm([(1,2,3,4),(1,2,5),(3,4,5)])


def cover6() -> List[Block]:
    return _norm([(1,2,3,4),(1,2,5,6),(3,4,5,6)])


def cover8() -> List[Block]:
    # Audited source Appendix B.2.
    return _norm([
        (1,2,3,4),(1,2,5,6),(1,2,7,8),
        (3,5,7),(4,5,8),(3,6,8),(4,6,7),
    ])


def cover10() -> List[Block]:
    return _norm([
        (1,2,5),(2,3,10),(4,7,10),
        (1,3,7),(2,4,8),(5,7,8),
        (1,4,9),(3,8,9),(5,9,10),
        (1,6,8,10),(2,6,7,9),(3,4,5,6),
    ])


def cover17() -> List[Block]:
    quads = [
        (1, 2, 4, 13), (1, 2, 14, 16), (1, 3, 5, 15),
        (1, 3, 7, 11), (1, 6, 8, 9), (1, 10, 12, 17),
        (2, 3, 9, 17), (4, 5, 8, 16), (4, 6, 11, 12),
        (4, 7, 9, 10), (5, 6, 13, 17), (5, 7, 12, 14),
        (6, 10, 14, 15), (7, 8, 13, 15), (8, 11, 14, 17),
        (9, 12, 15, 16), (10, 11, 13, 16),
    ]
    triples = [
        (2, 5, 10), (2, 6, 7), (2, 8, 12), (2, 11, 15),
        (3, 4, 14), (3, 6, 16), (3, 8, 10), (3, 12, 13),
        (4, 15, 17), (5, 9, 11), (7, 16, 17), (9, 13, 14),
    ]
    return _norm(quads + triples)


def cover18() -> List[Block]:
    quads = [
        (1,2,10,17),(2,4,5,7),(5,9,13,18),
        (1,3,5,15),(2,6,14,16),(5,11,16,17),
        (1,4,9,16),(2,9,12,15),(6,8,9,17),
        (1,6,7,13),(3,12,16,18),(6,11,15,18),
        (1,8,11,12),(4,12,13,14),(7,9,11,14),
        (2,3,11,13),(5,6,10,12),(8,10,13,16),
    ]
    triples = [
        (1,14,18),(3,14,17),(7,10,18),
        (2,8,18),(4,8,15),(7,12,17),
        (3,4,6),(4,10,11),(7,15,16),
        (3,7,8),(4,17,18),(10,14,15),
        (3,9,10),(5,8,14),(13,15,17),
    ]
    return _norm(quads+triples)


def cover19() -> List[Block]:
    quads = [
        (1,8,9,10),(2,9,11,16),(4,5,9,18),(7,8,14,18),
        (1,11,12,13),(2,10,12,18),(4,12,16,19),(7,9,13,19),
        (1,14,15,16),(3,4,10,17),(5,8,16,17),(9,12,15,17),
        (1,17,18,19),(3,6,9,14),(5,10,13,15),(10,11,14,19),
        (2,4,7,15),(3,8,15,19),(6,7,10,16),
        (2,5,6,19),(3,13,16,18),(6,11,15,18),
    ]
    triples = [
        (1,2,3),(3,7,12),(7,11,17),
        (1,4,6),(4,8,11),
        (1,5,7),(4,13,14),
        (2,8,13),(5,12,14),
        (2,14,17),(6,8,12),
        (3,5,11),(6,13,17),
    ]
    return _norm(quads+triples)


@lru_cache(maxsize=1)
def _pbd22_hole7_cached() -> Tuple[Tuple[Block, ...], Block]:
    """Primitive PBD(22,{4,7*}) finite ingredient."""
    from . import kirkman
    external: List[Block] = []
    for z, cls in zip(range(16,23), kirkman.kirkman_triple_system(15)):
        external.extend(tuple(sorted((*T,z))) for T in cls)
    hole = tuple(range(16,23))
    return tuple(_norm(external)), hole


def pbd22_hole7() -> Tuple[List[Block], Block]:
    """External K4s and the seven-point hole of PBD(22,{4,7*})."""
    external, hole = _pbd22_hole7_cached()
    return list(external), hole


@lru_cache(maxsize=1)
def _pbd46_hole7_cached() -> Tuple[Tuple[Block, ...], Block]:
    """Brouwer's cyclic PBD(46,{4,7*}) finite ingredient."""
    q = 13
    n = 46

    def P(i: int, j: int) -> int:
        return 1 + (i % 3) * q + (j % q)

    def H(a: int, i: int) -> int:
        return 3*q + 1 + (a % 2) * 3 + (i % 3)

    INF = n
    forms = (
        lambda i,j:(P(i,j+1),P(i,j+3),P(i,j+9),P(i+1,j)),
        lambda i,j:(P(i,j+2),P(i,j+6),P(i,j+5),P(i+1,j)),
        lambda i,j:(P(i,j),P(i+1,j+1),P(i+2,j+4),H(0,i)),
        lambda i,j:(P(i,j),P(i+1,j+2),P(i+2,j+7),H(1,i)),
        lambda i,j:(P(0,j),P(1,j),P(2,j),INF),
    )
    blocks = set()
    for i in range(3):
        for j in range(q):
            for f in forms:
                blocks.add(tuple(sorted(f(i,j))))
    hole = tuple([H(a,i) for a in range(2) for i in range(3)] + [INF])
    return tuple(sorted(blocks)), hole


def pbd46_hole7() -> Tuple[List[Block], Block]:
    """External K4s and the seven-point hole of PBD(46,{4,7*})."""
    external, hole = _pbd46_hole7_cached()
    return list(external), hole


__all__ = [
    "relabel","fano7","sts9","cover5","cover6","cover8","cover10",
    "cover17","cover18","cover19","pbd22_hole7","pbd46_hole7",
]
