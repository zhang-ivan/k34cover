"""Constructive pieces from W. H. Mills, *On the Covering of Pairs by
Quadruples II* (JCTA 15, 1973, 138--166).

This module is intentionally separate from the K3/K4 covering front-end.  Mills'
optimal K4 coverings of orders 7 or 10 modulo 12 are the ingredient used by
Colbourn--Rosa--Stinson to obtain the optimum {K3,K4}-PBDs in residue classes
6 and 9 modulo 12 by deleting an endpoint of the unique repeated pair.

Only deterministic constructions are implemented; there is no search at run time.
The current implementation contains Mills' class-10 seeds 22, 34, 70, 82,
all eleven finite class-7 base orders, Lemmas 2--4, and the finite non-MacNeish
TD(4,14) ingredient required at order 58.  In particular the Mills backend for
the class-7 orders needed by the {K3,K4} residue-6/9 construction is complete.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

from . import transversal

Block = Tuple[int, int, int, int]
Edge = Tuple[int, int]


def _norm(blocks: Iterable[Sequence[int]]) -> List[Block]:
    return sorted(tuple(sorted(map(int, b))) for b in blocks)


def mills_lower_bound(n: int) -> int:
    """Schönheim/Fort--Hedlund lower bound L(n)=ceil(n/4*ceil((n-1)/3))."""
    inner = (n - 1 + 2) // 3
    return (n * inner + 3) // 4


def analyse_k4_cover(n: int, blocks: Iterable[Sequence[int]]) -> Tuple[List[Edge], List[Edge]]:
    """Return (missing edges, repeated edge occurrences) for a K4 cover."""
    mult: Counter[Edge] = Counter()
    b = list(blocks)
    for raw in b:
        if len(raw) != 4 or len(set(raw)) != 4:
            raise ValueError(f"not a K4 block: {raw}")
        if min(raw) < 1 or max(raw) > n:
            raise ValueError(f"vertex outside 1..{n}: {raw}")
        for x, y in combinations(sorted(raw), 2):
            mult[(x, y)] += 1
    expected_edges = n * (n - 1) // 2
    if len(mult) == expected_edges:
        missing: List[Edge] = []
    else:
        missing = [
            (x, y)
            for x in range(1, n + 1)
            for y in range(x + 1, n + 1)
            if (x, y) not in mult
        ]
    repeated: List[Edge] = []
    for e, count in mult.items():
        if count > 1:
            repeated.extend([e] * (count - 1))
    repeated.sort()
    return missing, repeated


def check_mills_cover(n: int, blocks: Iterable[Sequence[int]]) -> bool:
    b = list(blocks)
    missing, repeated = analyse_k4_cover(n, b)
    assert not missing, f"K4 cover of {n} misses {missing[:5]}"
    assert len(b) == mills_lower_bound(n), f"{len(b)} blocks, expected L({n})={mills_lower_bound(n)}"
    # For n=7,10 mod12 and n not 7,10,19, Mills proves the excess is exactly
    # one pair covered four times, i.e. that edge occurs three times in this list.
    if n % 12 in (7, 10) and n not in (7, 10, 19):
        assert len(repeated) == 3, f"expected excess size 3, got {len(repeated)}"
        assert len(set(repeated)) == 1, f"expected one repeated pair, got {repeated}"
    return True


def k4_seed22() -> List[Block]:
    """Mills' explicit 39-block optimum cover of order 22 (paper II, p.144)."""
    rows = [
        ((1,2,3,4),(4,7,11,19)),
        ((1,2,5,6),(4,8,15,21)),
        ((1,2,7,8),(4,9,12,14)),
        ((1,2,9,10),(4,10,13,16)),
        ((1,11,12,13),(5,7,14,21)),
        ((1,14,15,16),(5,8,13,17)),
        ((1,17,18,19),(5,9,15,19)),
        ((1,20,21,22),(5,10,12,22)),
        ((2,11,14,17),(6,7,16,20)),
        ((2,12,15,20),(6,8,12,19)),
        ((2,13,18,21),(6,9,11,21)),
        ((2,16,19,22),(6,10,14,18)),
        ((3,5,11,16),(7,9,13,22)),
        ((3,6,13,15),(7,10,15,17)),
        ((3,7,12,18),(8,9,16,18)),
        ((3,8,14,22),(8,10,11,20)),
        ((3,9,17,20),(11,15,18,22)),
        ((3,10,19,21),(12,16,17,21)),
        ((4,5,18,20),(13,14,19,20)),
    ]
    blocks = [b for pair in rows for b in pair]
    blocks.append((4,6,17,22))
    return _norm(blocks)


def k4_seed34() -> List[Block]:
    """Mills' structured 94-block optimum cover of order 34 (paper II, pp.144--145)."""
    X, Y = 33, 34

    def P(i: int, j: int) -> int:
        # paper i=1..8, j in Z4
        return (i - 1) * 4 + (j % 4) + 1

    blocks: List[Block] = []
    for i in (1, 2):
        for j in (0, 1):
            blocks.append((X, Y, P(i,j), P(i,j+2)))
    for i in range(3, 9):
        blocks.append(tuple(P(i,j) for j in range(4)))

    forms: List[Callable[[int], Tuple[int, ...]]] = [
        lambda j:(P(1,j),P(1,j+1),P(2,j),P(3,j)),
        lambda j:(P(2,j),P(2,j+1),P(5,j),P(7,j)),
        lambda j:(P(1,j),P(2,j+1),P(4,j),P(5,j+2)),
        lambda j:(P(1,j),P(2,j+2),P(4,j+2),P(6,j)),
        lambda j:(P(1,j),P(3,j+1),P(4,j+1),P(7,j)),
        lambda j:(P(1,j),P(3,j+2),P(4,j+3),P(8,j)),
        lambda j:(P(1,j),P(5,j),P(6,j+2),P(7,j+1)),
        lambda j:(P(1,j),P(5,j+1),P(6,j+1),P(8,j+2)),
        lambda j:(P(1,j),P(5,j+3),P(7,j+2),P(8,j+3)),
        lambda j:(P(1,j),P(6,j+3),P(7,j+3),P(8,j+1)),
        lambda j:(P(2,j),P(3,j+2),P(5,j+2),P(6,j+3)),
        lambda j:(P(2,j),P(3,j+1),P(6,j+1),P(8,j+1)),
        lambda j:(P(2,j),P(3,j+3),P(7,j+1),P(8,j)),
        lambda j:(P(2,j),P(4,j+1),P(6,j),P(8,j+3)),
        lambda j:(P(2,j),P(4,j+2),P(7,j+2),P(8,j+2)),
        lambda j:(P(3,j),P(4,j+2),P(5,j+3),P(6,j+2)),
        lambda j:(P(3,j),P(4,j+3),P(5,j+2),P(7,j)),
        lambda j:(X,P(3,j),P(5,j+1),P(8,j+3)),
        lambda j:(X,P(4,j),P(6,j+1),P(7,j+2)),
        lambda j:(Y,P(3,j),P(6,j+3),P(7,j+1)),
        lambda j:(Y,P(4,j),P(5,j),P(8,j+3)),
    ]
    for form in forms:
        for j in range(4):
            blocks.append(form(j))
    return _norm(blocks)



def k4_seed31() -> List[Block]:
    """Mills' explicit 78-block optimum cover of order 31 (paper II, pp.147--148)."""
    X = 31
    P = lambda i,j: 2*(i-1) + (j % 2) + 1
    blocks: List[Block] = [
        (P(1,0),P(1,1),P(4,0),P(4,1)),
        (P(1,0),P(1,1),P(5,0),P(5,1)),
        (P(2,0),P(2,1),P(6,0),P(6,1)),
        (P(3,0),P(3,1),P(7,0),P(7,1)),
    ]
    for i in range(4,8):
        blocks.append((P(2*i,0),P(2*i,1),P(2*i+1,0),P(2*i+1,1)))
    forms: List[Callable[[int],Tuple[int,...]]] = [
        lambda j:(P(1,0),P(1,1),P(2,j),P(3,j+1)),
        lambda j:(X,P(1,j),P(8,j+1),P(10,j+1)),
        lambda j:(X,P(2,j),P(3,j),P(4,j+1)),
        lambda j:(X,P(5,j),P(12,j),P(14,j)),
        lambda j:(X,P(6,j),P(7,j+1),P(13,j+1)),
        lambda j:(X,P(9,j),P(11,j),P(15,j+1)),
        lambda j:(P(1,j),P(6,j),P(8,j),P(12,j)),
        lambda j:(P(1,j),P(6,j+1),P(11,j),P(14,j)),
        lambda j:(P(1,j),P(7,j),P(9,j),P(12,j+1)),
        lambda j:(P(1,j),P(7,j+1),P(10,j),P(15,j)),
        lambda j:(P(1,j),P(9,j+1),P(13,j),P(14,j+1)),
        lambda j:(P(1,j),P(11,j+1),P(13,j+1),P(15,j+1)),
        lambda j:(P(2,j),P(4,j),P(5,j),P(15,j+1)),
        lambda j:(P(2,j),P(5,j+1),P(8,j+1),P(13,j+1)),
        lambda j:(P(2,j),P(7,j),P(8,j),P(11,j+1)),
        lambda j:(P(2,j),P(7,j+1),P(9,j),P(14,j+1)),
        lambda j:(P(2,j),P(9,j+1),P(11,j),P(12,j+1)),
        lambda j:(P(2,j),P(10,j+1),P(12,j),P(15,j)),
        lambda j:(P(2,j),P(10,j),P(13,j),P(14,j)),
        lambda j:(P(3,j),P(4,j),P(11,j),P(12,j)),
        lambda j:(P(3,j),P(5,j),P(9,j+1),P(13,j+1)),
        lambda j:(P(3,j),P(5,j+1),P(11,j+1),P(14,j)),
        lambda j:(P(3,j),P(6,j+1),P(9,j),P(10,j+1)),
        lambda j:(P(3,j),P(6,j),P(13,j),P(15,j+1)),
        lambda j:(P(3,j),P(8,j+1),P(10,j),P(14,j+1)),
        lambda j:(P(3,j),P(8,j),P(12,j+1),P(15,j)),
        lambda j:(P(4,j),P(5,j+1),P(9,j+1),P(10,j+1)),
        lambda j:(P(4,j),P(6,j+1),P(8,j),P(14,j+1)),
        lambda j:(P(4,j),P(6,j),P(9,j),P(15,j)),
        lambda j:(P(4,j),P(7,j),P(10,j),P(13,j+1)),
        lambda j:(P(4,j),P(7,j+1),P(12,j+1),P(14,j)),
        lambda j:(P(4,j),P(8,j+1),P(11,j+1),P(13,j)),
        lambda j:(P(5,j),P(6,j+1),P(7,j+1),P(11,j+1)),
        lambda j:(P(5,j),P(6,j),P(10,j+1),P(12,j+1)),
        lambda j:(P(5,j),P(7,j),P(8,j+1),P(15,j)),
    ]
    for form in forms:
        for j in range(2):
            blocks.append(form(j))
    return _norm(blocks)


def k4_seed43() -> List[Block]:
    """Mills' explicit 151-block optimum cover of order 43 (paper II, pp.148--149)."""
    X = 43
    Z = lambda j: 41 + (j % 2)
    P = lambda i,j,k: 4*(i-1) + 2*(j % 2) + (k % 2) + 1
    blocks: List[Block] = []
    for j in range(2):
        blocks.append((X,Z(j),P(3,j+1,0),P(3,j+1,1)))
        blocks.append((Z(0),Z(1),P(1,j,0),P(1,j+1,1)))
        blocks.append((P(1,j,0),P(1,j,1),P(2,j+1,0),P(2,j+1,1)))
        blocks.append((P(2,j,0),P(2,j+1,1),P(3,j,1),P(3,j+1,0)))
    for k in range(2):
        blocks.append((Z(0),Z(1),P(2,0,k),P(2,1,k)))
        blocks.append((P(1,0,k),P(1,1,k),P(3,0,k+1),P(3,1,k+1)))
    for i in range(4,11):
        blocks.append((P(i,0,0),P(i,0,1),P(i,1,0),P(i,1,1)))

    forms: List[Callable[[int,int],Tuple[int,...]]] = [
        lambda j,k:(P(1,j,k),P(2,j,k),P(5,j,k),P(8,j,k)),
        lambda j,k:(P(1,j,k),P(3,j,k),P(6,j,k),P(9,j,k)),
        lambda j,k:(P(1,j,k),P(3,j+1,k),P(7,j,k),P(9,j,k+1)),
        lambda j,k:(P(1,j,k),P(4,j,k),P(5,j+1,k),P(10,j,k)),
        lambda j,k:(P(1,j,k),P(4,j+1,k),P(5,j,k+1),P(10,j,k+1)),
        lambda j,k:(P(1,j,k),P(4,j+1,k+1),P(7,j+1,k+1),P(8,j+1,k+1)),
        lambda j,k:(P(1,j,k),P(5,j+1,k+1),P(8,j,k+1),P(9,j+1,k)),
        lambda j,k:(P(1,j,k),P(6,j+1,k+1),P(7,j,k+1),P(8,j+1,k)),
        lambda j,k:(P(1,j,k),P(6,j,k+1),P(7,j+1,k),P(10,j+1,k+1)),
        lambda j,k:(P(1,j,k),P(6,j+1,k),P(9,j+1,k+1),P(10,j+1,k)),
        lambda j,k:(P(2,j,k),P(3,j,k),P(7,j,k+1),P(10,j+1,k+1)),
        lambda j,k:(P(2,j,k),P(3,j+1,k+1),P(8,j+1,k+1),P(10,j+1,k)),
        lambda j,k:(P(2,j,k),P(4,j+1,k),P(6,j+1,k),P(9,j,k)),
        lambda j,k:(P(2,j,k),P(4,j+1,k+1),P(6,j,k),P(9,j+1,k+1)),
        lambda j,k:(P(2,j,k),P(4,j,k+1),P(6,j+1,k+1),P(10,j,k)),
        lambda j,k:(P(2,j,k),P(5,j,k+1),P(7,j+1,k),P(9,j+1,k)),
        lambda j,k:(P(2,j,k),P(5,j+1,k+1),P(7,j+1,k+1),P(9,j,k+1)),
        lambda j,k:(P(2,j,k),P(5,j+1,k),P(8,j,k+1),P(10,j,k+1)),
        lambda j,k:(P(2,j,k),P(6,j,k+1),P(7,j,k),P(8,j+1,k)),
        lambda j,k:(P(3,j,k),P(4,j,k),P(5,j,k+1),P(9,j,k+1)),
        lambda j,k:(P(3,j,k),P(4,j+1,k+1),P(7,j,k),P(8,j,k+1)),
        lambda j,k:(P(3,j,k),P(4,j+1,k),P(7,j+1,k+1),P(10,j,k)),
        lambda j,k:(P(3,j,k),P(4,j,k+1),P(8,j+1,k),P(9,j+1,k)),
        lambda j,k:(P(3,j,k),P(5,j+1,k),P(6,j,k+1),P(8,j+1,k+1)),
        lambda j,k:(P(3,j,k),P(5,j+1,k+1),P(6,j+1,k+1),P(10,j+1,k)),
        lambda j,k:(Z(j),P(3,j,k),P(5,j,k),P(6,j+1,k)),
        lambda j,k:(Z(j),P(4,j+1,k),P(5,j+1,k),P(7,j,k)),
        lambda j,k:(Z(j),P(4,j,k),P(6,j,k+1),P(8,j,k+1)),
        lambda j,k:(Z(j),P(7,j+1,k),P(9,j,k+1),P(10,j+1,k)),
        lambda j,k:(Z(j),P(8,j+1,k),P(9,j+1,k+1),P(10,j,k+1)),
        lambda j,k:(X,P(1,j,k),P(2,j,k+1),P(4,j,k+1)),
        lambda j,k:(X,P(5,j,k),P(6,j,k+1),P(7,j,k+1)),
        lambda j,k:(X,P(8,j,k),P(9,j+1,k),P(10,j+1,k)),
    ]
    for form in forms:
        for j in range(2):
            for k in range(2):
                blocks.append(form(j,k))
    return _norm(blocks)


def k4_seed55() -> List[Block]:
    """Mills' explicit 248-block optimum cover of order 55 (paper II, pp.150--152)."""
    X = 55
    Z = lambda j: 53 + (j % 2)
    P = lambda i,j,k: 4*(i-1) + 2*(j % 2) + (k % 2) + 1
    blocks: List[Block] = []
    for j in range(2):
        blocks.append((X,Z(j),P(3,j+1,0),P(3,j+1,1)))
        blocks.append((Z(0),Z(1),P(1,j,0),P(1,j+1,1)))
        blocks.append((P(1,j,0),P(1,j,1),P(2,j+1,0),P(2,j+1,1)))
        blocks.append((P(2,j,0),P(2,j+1,1),P(3,j,1),P(3,j+1,0)))
    for k in range(2):
        blocks.append((Z(0),Z(1),P(2,0,k),P(2,1,k)))
        blocks.append((P(1,0,k),P(1,1,k),P(3,0,k+1),P(3,1,k+1)))
    for i in range(7,14):
        blocks.append((P(i,0,0),P(i,0,1),P(i,1,0),P(i,1,1)))
    blocks.extend([
        (P(4,0,0),P(4,0,1),P(4,1,0),P(4,1,1)),
        (P(4,0,0),P(5,0,1),P(5,1,0),P(5,1,1)),
        (P(4,0,0),P(6,0,1),P(6,1,0),P(6,1,1)),
        (P(5,0,0),P(4,0,1),P(5,1,0),P(6,1,1)),
        (P(5,0,0),P(5,0,1),P(6,1,0),P(4,1,1)),
        (P(5,0,0),P(6,0,1),P(4,1,0),P(5,1,1)),
        (P(6,0,0),P(4,0,1),P(6,1,0),P(5,1,1)),
        (P(6,0,0),P(5,0,1),P(4,1,0),P(6,1,1)),
        (P(6,0,0),P(6,0,1),P(5,1,0),P(4,1,1)),
    ])
    forms: List[Callable[[int,int],Tuple[int,...]]] = [
        lambda j,k:(P(1,j,k),P(2,j,k),P(3,j,k),P(4,j,k)),
        lambda j,k:(P(1,j,k),P(3,j+1,k),P(4,j,k+1),P(9,j,k)),
        lambda j,k:(P(1,j,k),P(4,j+1,k),P(6,j+1,k),P(10,j,k)),
        lambda j,k:(P(1,j,k),P(5,j,k),P(7,j,k),P(8,j,k)),
        lambda j,k:(P(1,j,k),P(5,j+1,k),P(7,j,k+1),P(12,j,k)),
        lambda j,k:(P(1,j,k),P(5,j+1,k+1),P(8,j+1,k),P(13,j,k)),
        lambda j,k:(P(1,j,k),P(5,j,k+1),P(11,j,k),P(12,j+1,k)),
        lambda j,k:(P(1,j,k),P(6,j,k),P(9,j+1,k),P(11,j,k+1)),
        lambda j,k:(P(1,j,k),P(6,j+1,k+1),P(10,j+1,k+1),P(11,j+1,k+1)),
        lambda j,k:(P(1,j,k),P(6,j,k+1),P(11,j+1,k),P(13,j,k+1)),
        lambda j,k:(P(1,j,k),P(7,j+1,k+1),P(9,j+1,k+1),P(12,j+1,k+1)),
        lambda j,k:(P(1,j,k),P(7,j+1,k),P(9,j,k+1),P(13,j+1,k+1)),
        lambda j,k:(P(1,j,k),P(8,j+1,k+1),P(10,j+1,k),P(12,j,k+1)),
        lambda j,k:(P(1,j,k),P(8,j,k+1),P(10,j,k+1),P(13,j+1,k)),
        lambda j,k:(P(2,j,k),P(3,j+1,k+1),P(8,j,k),P(11,j+1,k)),
        lambda j,k:(P(2,j,k),P(4,j+1,k+1),P(10,j+1,k+1),P(12,j+1,k)),
        lambda j,k:(P(2,j,k),P(4,j,k+1),P(11,j+1,k+1),P(13,j+1,k+1)),
        lambda j,k:(P(2,j,k),P(5,j+1,k),P(9,j,k+1),P(11,j,k+1)),
        lambda j,k:(P(2,j,k),P(5,j,k+1),P(9,j+1,k+1),P(12,j,k)),
        lambda j,k:(P(2,j,k),P(5,j+1,k+1),P(9,j+1,k),P(12,j+1,k+1)),
        lambda j,k:(P(2,j,k),P(5,j,k),P(10,j+1,k),P(13,j+1,k)),
        lambda j,k:(P(2,j,k),P(6,j,k),P(7,j+1,k+1),P(13,j,k+1)),
        lambda j,k:(P(2,j,k),P(6,j+1,k),P(7,j,k),P(13,j,k)),
        lambda j,k:(P(2,j,k),P(6,j,k+1),P(8,j+1,k),P(10,j,k)),
        lambda j,k:(P(2,j,k),P(6,j+1,k+1),P(8,j,k+1),P(12,j,k+1)),
        lambda j,k:(P(2,j,k),P(7,j,k+1),P(8,j+1,k+1),P(11,j,k)),
        lambda j,k:(P(2,j,k),P(7,j+1,k),P(9,j,k),P(10,j,k+1)),
        lambda j,k:(P(3,j,k),P(4,j+1,k),P(12,j,k),P(13,j+1,k+1)),
        lambda j,k:(P(3,j,k),P(5,j,k),P(9,j,k),P(13,j,k)),
        lambda j,k:(P(3,j,k),P(5,j+1,k),P(10,j+1,k+1),P(11,j+1,k)),
        lambda j,k:(P(3,j,k),P(5,j,k+1),P(10,j,k+1),P(11,j+1,k+1)),
        lambda j,k:(P(3,j,k),P(5,j+1,k+1),P(10,j,k),P(13,j+1,k)),
        lambda j,k:(P(3,j,k),P(6,j+1,k),P(7,j+1,k),P(13,j,k+1)),
        lambda j,k:(P(3,j,k),P(6,j,k+1),P(8,j,k+1),P(12,j+1,k)),
        lambda j,k:(P(3,j,k),P(6,j+1,k+1),P(8,j+1,k),P(12,j+1,k+1)),
        lambda j,k:(P(3,j,k),P(6,j,k),P(9,j+1,k+1),P(12,j,k+1)),
        lambda j,k:(P(3,j,k),P(7,j+1,k+1),P(8,j,k),P(11,j,k)),
        lambda j,k:(P(3,j,k),P(7,j,k),P(9,j,k+1),P(10,j+1,k)),
        lambda j,k:(P(4,j,k),P(7,j+1,k),P(10,j+1,k+1),P(11,j,k)),
        lambda j,k:(P(4,j,k),P(7,j,k+1),P(10,j,k+1),P(12,j+1,k+1)),
        lambda j,k:(P(4,j,k),P(7,j+1,k+1),P(11,j+1,k+1),P(12,j,k)),
        lambda j,k:(P(4,j,k),P(8,j,k),P(9,j,k),P(11,j,k+1)),
        lambda j,k:(P(4,j,k),P(8,j,k+1),P(9,j+1,k+1),P(13,j,k)),
        lambda j,k:(P(4,j,k),P(8,j+1,k+1),P(9,j+1,k),P(13,j+1,k+1)),
        lambda j,k:(Z(j),P(3,j,k),P(4,j,k+1),P(7,j,k+1)),
        lambda j,k:(Z(j),P(4,j+1,k),P(5,j+1,k),P(8,j,k)),
        lambda j,k:(Z(j),P(5,j,k),P(7,j+1,k),P(8,j+1,k+1)),
        lambda j,k:(Z(j),P(6,j,k),P(9,j,k+1),P(10,j+1,k+1)),
        lambda j,k:(Z(j),P(6,j+1,k),P(9,j+1,k),P(11,j,k)),
        lambda j,k:(Z(j),P(10,j,k),P(12,j,k),P(13,j,k+1)),
        lambda j,k:(Z(j),P(11,j+1,k),P(12,j+1,k+1),P(13,j+1,k+1)),
        lambda j,k:(X,P(1,j,k),P(2,j,k+1),P(4,j+1,k+1)),
        lambda j,k:(X,P(5,j,k),P(6,j,k),P(7,j,k+1)),
        lambda j,k:(X,P(8,j,k),P(9,j+1,k+1),P(10,j+1,k+1)),
        lambda j,k:(X,P(11,j,k),P(12,j,k),P(13,j+1,k)),
    ]
    assert len(forms) == 55
    for form in forms:
        for j in range(2):
            for k in range(2):
                blocks.append(form(j,k))
    return _norm(blocks)


def k4_seed79() -> List[Block]:
    """Mills' structured 514-block optimum cover of order 79 (paper II, pp.152--153)."""
    A = lambda a: a
    P = lambda i,j: 13 + (i-1)*11 + (j % 11) + 1
    blocks: List[Block] = []
    blocks.extend(_relabel_blocks(k4_seed22(), [P(i,j) for i in (1,2) for j in range(11)]))
    from . import bibd4
    blocks.extend(_relabel_blocks(bibd4.bibd4(13), list(range(1,14))))
    forms: List[Callable[[int],Tuple[int,...]]] = [
        lambda j:(P(3,j),P(3,j+1),P(5,j),P(5,j+2)),
        lambda j:(P(3,j),P(3,j+2),P(6,j),P(6,j+1)),
        lambda j:(P(4,j),P(4,j+1),P(5,j),P(5,j+3)),
        lambda j:(P(4,j),P(4,j+2),P(6,j),P(6,j+3)),
        lambda j:(P(1,j),P(3,j),P(4,j),P(4,j+3)),
        lambda j:(P(1,j),P(3,j+1),P(4,j+2),P(4,j+6)),
        lambda j:(P(1,j),P(5,j),P(5,j+1),P(6,j)),
        lambda j:(P(1,j),P(5,j+2),P(5,j+6),P(6,j+3)),
        lambda j:(P(1,j),P(5,j+3),P(6,j+1),P(6,j+5)),
        lambda j:(P(1,j),P(5,j+4),P(6,j+7),P(6,j+9)),
        lambda j:(P(2,j),P(3,j),P(3,j+3),P(5,j+6)),
        lambda j:(P(2,j),P(3,j+1),P(3,j+5),P(4,j)),
        lambda j:(P(2,j),P(3,j+2),P(3,j+7),P(4,j+4)),
        lambda j:(P(2,j),P(4,j+1),P(4,j+6),P(6,j)),
        lambda j:(P(2,j),P(4,j+2),P(5,j+3),P(5,j+8)),
        lambda j:(P(2,j),P(3,j+4),P(6,j+1),P(6,j+6)),
        lambda j:(A(1),P(1,j),P(3,j+3),P(4,j+1)),
        lambda j:(A(1),P(2,j),P(5,j+1),P(6,j+5)),
        lambda j:(A(2),P(1,j),P(3,j+4),P(4,j+8)),
        lambda j:(A(2),P(2,j),P(5,j+2),P(6,j+8)),
        lambda j:(A(3),P(1,j),P(3,j+5),P(5,j+9)),
        lambda j:(A(3),P(2,j),P(4,j+7),P(6,j+3)),
        lambda j:(A(4),P(1,j),P(3,j+8),P(5,j+5)),
        lambda j:(A(4),P(2,j),P(4,j+8),P(6,j+10)),
        lambda j:(A(5),P(1,j),P(3,j+9),P(5,j+7)),
        lambda j:(A(5),P(2,j),P(4,j+9),P(6,j+4)),
        lambda j:(A(6),P(1,j),P(3,j+6),P(6,j+10)),
        lambda j:(A(6),P(2,j),P(4,j+3),P(5,j+10)),
        lambda j:(A(7),P(1,j),P(3,j+7),P(6,j+2)),
        lambda j:(A(7),P(2,j),P(4,j+5),P(5,j+9)),
        lambda j:(A(8),P(1,j),P(3,j+10),P(6,j+6)),
        lambda j:(A(8),P(2,j),P(4,j+10),P(5,j+7)),
        lambda j:(A(9),P(1,j),P(4,j+5),P(5,j+10)),
        lambda j:(A(9),P(2,j),P(3,j+6),P(6,j+9)),
        lambda j:(A(10),P(1,j),P(4,j+10),P(5,j+8)),
        lambda j:(A(10),P(2,j),P(3,j+8),P(6,j+2)),
        lambda j:(A(11),P(1,j),P(4,j+4),P(6,j+8)),
        lambda j:(A(11),P(2,j),P(3,j+9),P(5,j+5)),
        lambda j:(A(12),P(1,j),P(4,j+7),P(6,j+4)),
        lambda j:(A(12),P(2,j),P(3,j+10),P(5,j+4)),
        lambda j:(A(13),P(1,j),P(3,j+2),P(4,j+9)),
        lambda j:(A(13),P(2,j),P(5,j),P(6,j+7)),
    ]
    assert len(forms) == 42
    for form in forms:
        for j in range(11):
            blocks.append(form(j))
    return _norm(blocks)



def k4_seed91() -> List[Block]:
    """Mills' 683-block optimum cover of order 91 (paper II, pp.153--155).

    Mills takes the point set I_22 union (Z_3 x Z_23).  This is the one
    class-7 finite seed in his list that was *not* found by the CDC 6600;
    the displayed construction is developed arithmetically exactly as in
    the paper.  All second coordinates below are reduced modulo 23 and
    all first coordinates of ordered pairs modulo 3.
    """
    A = lambda a: a                         # the points 1,...,22
    P = lambda j,k: 23 + (j % 3)*23 + (k % 23)  # labels 23,...,91

    blocks: List[Block] = list(k4_seed22())

    # 69 blocks of each of two forms: j in Z_3, k in Z_23.
    for j in range(3):
        for k in range(23):
            blocks.append((P(j,k), P(j,k+1), P(j,k+4), P(j,k+9)))
            blocks.append((P(j-1,k), P(j,k+9), P(j,k+15), P(j,k+22)))

    # 63 blocks: j in Z_3, 0<=k<=6, 1<=i<=3.
    for j in range(3):
        for k in range(7):
            for i in range(1,4):
                blocks.append((A(i), P(j,18*k-12*i+6),
                                P(j+1,18*k-12*i+12),
                                P(j,18*k-12*i+18)))

    # Six blocks with k=18 or 21 and j in Z_3.
    for k in (18,21):
        for j in range(3):
            blocks.append((A(4), P(j,6*k-12), P(j+1,6*k-6), P(j,6*k)))

    # Six blocks with k=0 or -1 and 1<=i<=3.
    for k in (0,-1):
        for i in range(1,4):
            blocks.append((A(i), P(0,6*k-12*i), P(1,6*k-12*i), P(2,6*k-12*i)))

    # Seventeen blocks, -1<=k<=15.
    for k in range(-1,16):
        blocks.append((A(4), P(0,6*k), P(1,6*k), P(2,6*k)))

    # 21 blocks of each of three forms: 0<=k<=6, 5<=i<=7.
    for k in range(7):
        for i in range(5,8):
            blocks.append((A(i), P(0,3*k-2*i+1), P(1,3*k-2*i+4), P(0,3*k-2*i+3)))
            blocks.append((A(i), P(1,3*k-2*i+3), P(2,3*k-2*i+6), P(1,3*k-2*i+5)))
            blocks.append((A(i), P(2,3*k-2*i+5), P(0,3*k-2*i+2), P(2,3*k-2*i+7)))

    # Two blocks of each of three forms, k=8 or 11.
    for k in (8,11):
        blocks.append((A(8), P(0,k),   P(1,k+3), P(0,k+2)))
        blocks.append((A(8), P(1,k+2), P(2,k+5), P(1,k+4)))
        blocks.append((A(8), P(2,k+4), P(0,k+1), P(2,k+6)))

    # Six blocks with 5<=i<=7 and k=0 or -1.
    for i in range(5,8):
        for k in (0,-1):
            blocks.append((A(i), P(0,k-2*i), P(1,k-2*i+2), P(2,k-2*i+4)))

    # Seventeen blocks, -9<=k<=7.
    for k in range(-9,8):
        blocks.append((A(8), P(0,k), P(1,k+2), P(2,k+4)))

    # Twenty-three blocks of each of the final fourteen forms (k in Z_23).
    tail = [
        (9,10,20), (10,11,22), (11,16,13), (12,18,9),
        (13,4,16), (14,7,11), (15,13,21), (16,20,2),
        (17,5,18), (18,8,15), (19,21,19), (20,19,12),
        (21,12,7), (22,14,10),
    ]
    for a,d1,d2 in tail:
        for k in range(23):
            blocks.append((A(a), P(0,k), P(1,k+d1), P(2,k+d2)))

    return _norm(blocks)

def _mills_structured_seed(n: int, m: int, specs: Sequence[Sequence[Tuple[str,int,int]]]) -> List[Block]:
    """Build Mills' tabulated class-7 seeds of orders 115,127,151,163,199.

    Mills writes the point set as T union (Z_3 x Z_r), where
    T = {X} union {[i,j] : i in Z_3, 1<=j<=m} and
    r=(n-3m-1)/3.  The supplied ``specs`` are the displayed orbit forms;
    each is developed for every i in Z_3 and k in Z_r.

    A spec entry is either ``('N',di,dk)`` for the point (i+di,k+dk),
    with both coordinates reduced modulo 3 and r, or ``('T',di,j)`` for
    the fixed point [i+di,j].  No search is involved.
    """
    if (n - 3*m - 1) % 3:
        raise ValueError("bad Mills structured-seed parameters")
    r = (n - 3*m - 1)//3
    if r <= 0:
        raise ValueError("Mills structured seed needs r>0")

    # Canonical global labels.  Put X first, then the 3m points of T, then
    # the 3r cyclic points.  The initial cover on T may be relabelled
    # arbitrarily because the orbit forms only require its pair coverage.
    X = 1
    T = lambda i,j: 2 + (i % 3)*m + (j-1)
    N = lambda i,k: 2 + 3*m + (i % 3)*r + (k % r)

    source_order = 3*m + 1
    source = mills_k4_cover(source_order)
    t_points = [X] + [T(i,j) for i in range(3) for j in range(1,m+1)]
    blocks: List[Block] = _relabel_blocks(source, t_points)

    # The r displayed blocks X,(0,k),(1,k),(2,k).
    for k in range(r):
        blocks.append((X, N(0,k), N(1,k), N(2,k)))

    for spec in specs:
        if len(spec) != 4:
            raise ValueError(f"orbit spec must have four entries: {spec}")
        for i in range(3):
            for k in range(r):
                B=[]
                for kind,a,b in spec:
                    if kind == 'N':
                        B.append(N(i+a,k+b))
                    elif kind == 'T':
                        B.append(T(i+a,b))
                    else:
                        raise ValueError(f"unknown Mills point kind {kind!r}")
                if len(set(B)) != 4:
                    raise AssertionError(f"degenerate developed block from {spec}, i={i}, k={k}")
                blocks.append(tuple(B))
    return _norm(blocks)


def _N(di: int, dk: int) -> Tuple[str,int,int]:
    return ('N', di, dk)


def _T(di: int, j: int) -> Tuple[str,int,int]:
    return ('T', di, j)


def k4_seed115() -> List[Block]:
    """Mills' cyclic 1093-block optimum cover of order 115 (paper II, pp.155--156)."""
    specs = [
        (_N(0,0),_N(0,1),_N(0,3),_N(0,10)),
        (_N(2,0),_N(0,1),_N(0,5),_N(0,17)),
        (_N(2,0),_N(0,2),_N(0,7),_N(0,15)),
        (_N(2,0),_N(0,18),_N(0,24),_N(0,4)),
        (_T(0,1),_N(0,0),_N(1,3),_N(2,9)),
        (_T(0,2),_N(0,0),_N(1,8),_N(2,17)),
        (_T(0,3),_N(0,0),_N(1,10),_N(2,2)),
        (_T(0,4),_N(0,0),_N(1,11),_N(2,5)),
        (_T(0,5),_N(0,0),_N(1,12),_N(2,1)),
        (_T(0,6),_N(0,0),_N(1,13),_N(2,3)),
        (_T(0,7),_N(0,0),_N(1,16),_N(2,4)),
    ]
    return _mills_structured_seed(115,7,specs)


def k4_seed127() -> List[Block]:
    """Mills' cyclic 1334-block optimum cover of order 127 (paper II, p.156)."""
    specs = [
        (_N(0,0),_N(0,1),_N(0,3),_N(0,7)),
        (_N(0,0),_N(0,5),_N(0,13),_N(0,23)),
        (_N(2,0),_N(0,1),_N(0,10),_N(0,21)),
        (_N(0,0),_N(1,2),_N(1,16),_N(2,6)),
        (_N(0,0),_N(1,17),_N(1,33),_N(2,32)),
        (_T(0,1),_N(0,0),_N(1,5),_N(2,11)),
        (_T(0,2),_N(0,0),_N(1,7),_N(2,15)),
        (_T(0,3),_N(0,0),_N(1,9),_N(2,21)),
        (_T(0,4),_N(0,0),_N(1,11),_N(2,3)),
        (_T(0,5),_N(0,0),_N(1,13),_N(2,4)),
        (_T(0,6),_N(0,0),_N(1,18),_N(2,5)),
        (_T(0,7),_N(0,0),_N(1,19),_N(2,7)),
    ]
    return _mills_structured_seed(127,7,specs)


def k4_seed151() -> List[Block]:
    """Mills' cyclic 1888-block optimum cover of order 151 (paper II, pp.156--157)."""
    specs = [
        (_N(2,0),_N(0,1),_N(0,2),_N(0,4)),
        (_N(2,0),_N(0,3),_N(0,7),_N(0,12)),
        (_N(2,0),_N(0,5),_N(0,11),_N(0,23)),
        (_N(2,0),_N(0,6),_N(0,13),_N(0,27)),
        (_N(2,0),_N(0,8),_N(0,16),_N(0,31)),
        (_N(2,0),_N(0,32),_N(0,42),_N(0,15)),
        (_N(2,0),_N(0,17),_N(0,28),_N(0,41)),
        (_T(0,1),_N(0,0),_N(1,9),_N(2,19)),
        (_T(0,2),_N(0,0),_N(1,14),_N(2,5)),
        (_T(0,3),_N(0,0),_N(1,18),_N(2,8)),
        (_T(0,4),_N(0,0),_N(1,19),_N(2,6)),
        (_T(0,5),_N(0,0),_N(1,20),_N(2,3)),
        (_T(0,6),_N(0,0),_N(1,21),_N(2,7)),
        (_T(0,7),_N(0,0),_N(1,22),_N(2,4)),
    ]
    return _mills_structured_seed(151,7,specs)


def k4_seed163() -> List[Block]:
    """Mills' cyclic 2201-block optimum cover of order 163 (paper II, p.157)."""
    specs = [
        (_N(0,0),_N(0,1),_N(0,3),_N(0,7)),
        (_N(0,0),_N(0,5),_N(0,15),_N(0,26)),
        (_N(2,0),_N(0,1),_N(0,9),_N(0,25)),
        (_N(2,0),_N(0,4),_N(0,13),_N(0,27)),
        (_N(2,0),_N(0,33),_N(0,2),_N(0,15)),
        (_T(0,1),_N(0,0),_N(1,3),_N(2,8)),
        (_T(0,2),_N(0,0),_N(1,6),_N(2,13)),
        (_T(0,3),_N(0,0),_N(1,8),_N(2,19)),
        (_T(0,4),_N(0,0),_N(1,10),_N(2,22)),
        (_T(0,5),_N(0,0),_N(1,14),_N(2,3)),
        (_T(0,6),_N(0,0),_N(1,16),_N(2,7)),
        (_T(0,7),_N(0,0),_N(1,17),_N(2,5)),
        (_T(0,8),_N(0,0),_N(1,18),_N(2,1)),
        (_T(0,9),_N(0,0),_N(1,19),_N(2,4)),
        (_T(0,10),_N(0,0),_N(1,20),_N(2,6)),
        (_T(0,11),_N(0,0),_N(1,22),_N(2,2)),
    ]
    return _mills_structured_seed(163,11,specs)


def k4_seed199() -> List[Block]:
    """Mills' cyclic 3284-block optimum cover of order 199 (paper II, pp.157--158)."""
    specs = [
        (_N(0,0),_N(0,1),_N(0,3),_N(0,7)),
        (_N(2,0),_N(0,1),_N(0,6),_N(0,14)),
        (_N(2,0),_N(0,2),_N(0,11),_N(0,29)),
        (_N(2,0),_N(0,3),_N(0,13),_N(0,32)),
        (_N(2,0),_N(0,4),_N(0,15),_N(0,35)),
        (_N(2,0),_N(0,5),_N(0,17),_N(0,38)),
        (_N(2,0),_N(0,7),_N(0,21),_N(0,37)),
        (_N(2,0),_N(0,16),_N(0,31),_N(0,48)),
        (_T(0,1),_N(0,0),_N(1,8),_N(2,27)),
        (_T(0,2),_N(0,0),_N(1,9),_N(2,19)),
        (_T(0,3),_N(0,0),_N(1,12),_N(2,1)),
        (_T(0,4),_N(0,0),_N(1,18),_N(2,4)),
        (_T(0,5),_N(0,0),_N(1,20),_N(2,8)),
        (_T(0,6),_N(0,0),_N(1,22),_N(2,6)),
        (_T(0,7),_N(0,0),_N(1,23),_N(2,10)),
        (_T(0,8),_N(0,0),_N(1,24),_N(2,9)),
        (_T(0,9),_N(0,0),_N(1,25),_N(2,3)),
        (_T(0,10),_N(0,0),_N(1,26),_N(2,5)),
        (_T(0,11),_N(0,0),_N(1,27),_N(2,2)),
    ]
    return _mills_structured_seed(199,11,specs)

def k4_seed259() -> List[Block]:
    """Mills' cyclic 5569-block optimum cover of order 259 (paper II, pp.158--159)."""
    specs = [
        (_N(0,0),_N(0,1),_N(0,3),_N(0,7)),
        (_N(0,0),_N(0,5),_N(0,13),_N(0,23)),
        (_N(0,0),_N(0,9),_N(0,30),_N(0,41)),
        (_N(0,0),_N(0,15),_N(0,31),_N(0,48)),
        (_N(2,0),_N(0,1),_N(0,13),_N(0,40)),
        (_N(2,0),_N(0,3),_N(0,17),_N(0,41)),
        (_N(2,0),_N(0,8),_N(0,28),_N(0,50)),
    ]
    tails = [
        (2,6),(5,11),(7,16),(10,21),(12,28),(14,29),(18,37),
        (20,41),(22,2),(23,1),(24,5),(25,12),(27,9),(29,14),
        (31,8),(32,7),(33,3),(34,10),(35,4),
    ]
    for j,(a,b) in enumerate(tails, start=1):
        specs.append((_T(0,j),_N(0,0),_N(1,a),_N(2,b)))
    return _mills_structured_seed(259,19,specs)


def _relabel_blocks(blocks: Iterable[Sequence[int]], points: Sequence[int]) -> List[Block]:
    """Relabel a design on 1..len(points) onto ``points``."""
    return _norm(tuple(points[x-1] for x in b) for b in blocks)


def _point_registry(keys: Iterable[object]) -> Tuple[Dict[object,int], List[object]]:
    ordered = list(keys)
    return {k:i+1 for i,k in enumerate(ordered)}, ordered


def k4_seed70() -> List[Block]:
    """Mills' structured optimum cover of order 70 (paper II, pp.145--146)."""
    keys = [('z',j) for j in range(22)]
    for i in range(2):
        keys.extend([('p',i,'z',j) for j in range(22)])
        keys.extend([('p',i,'X'),('p',i,'Y')])
    lab, _ = _point_registry(keys)
    Z = lambda j: lab[('z',j%22)]
    P = lambda i,j: lab[('p',i%2,'z',j%22)]
    PX = lambda i: lab[('p',i%2,'X')]
    PY = lambda i: lab[('p',i%2,'Y')]

    blocks: List[Block] = []
    blocks.extend(_relabel_blocks(k4_seed22(), [Z(j) for j in range(22)]))
    blocks.append((PX(0),PX(1),PY(0),PY(1)))
    for j in range(11):
        blocks.append((P(0,j),P(0,j+11),P(1,j),P(1,j+11)))

    forms: List[Callable[[int,int],Tuple[int,...]]] = [
        lambda i,j:(Z(j),P(i,j),P(i,j+2),P(i,j+5)),
        lambda i,j:(Z(j),P(i,j+3),P(i,j+4),P(i,j+10)),
        lambda i,j:(Z(j),P(i,j+11),P(i,j+15),P(i+1,j+16)),
        lambda i,j:(Z(j),P(i,j+6),P(i,j+20),P(i+1,j+18)),
        lambda i,j:(Z(j),P(i,j+21),P(i,j+8),P(i+1,j+12)),
        lambda i,j:(Z(j),P(i,j+7),P(i,j+17),P(i+1,j+14)),
        lambda i,j:(Z(j),PX(i),P(i,j+13),P(i+1,j+19)),
        lambda i,j:(Z(j),PY(i),P(i,j+1),P(i+1,j+9)),
    ]
    for form in forms:
        for i in range(2):
            for j in range(22):
                blocks.append(form(i,j))
    return _norm(blocks)


def k4_seed82() -> List[Block]:
    """Mills' structured optimum cover of order 82 (paper II, p.146)."""
    keys = [('z',j) for j in range(22)]
    keys += [('p',i,j) for i in range(2) for j in range(22)]
    keys += [('h',i,k) for i in range(2) for k in range(1,9)]
    lab, _ = _point_registry(keys)
    Z = lambda j: lab[('z',j%22)]
    P = lambda i,j: lab[('p',i%2,j%22)]
    H = lambda i,k: lab[('h',i%2,k)]

    blocks: List[Block] = []
    blocks.extend(_relabel_blocks(k4_seed22(), [Z(j) for j in range(22)]))
    from . import bibd4
    blocks.extend(_relabel_blocks(bibd4.bibd4(16), [H(i,k) for i in range(2) for k in range(1,9)]))
    for j in range(11):
        blocks.append((P(0,j),P(0,j+11),P(1,j),P(1,j+11)))

    forms: List[Callable[[int,int],Tuple[int,...]]] = [
        lambda i,j:(P(i,j),P(i,j+1),P(i,j+3),P(i,j+7)),
        lambda i,j:(Z(j),P(i,j),P(i,j+5),P(i,j+13)),
        lambda i,j:(Z(j),P(i,j+1),P(i,j+11),P(i+1,j+2)),
        lambda i,j:(Z(j),H(i,1),P(i,j+6),P(i+1,j+9)),
        lambda i,j:(Z(j),H(i,2),P(i,j+7),P(i+1,j+12)),
        lambda i,j:(Z(j),H(i,3),P(i,j+10),P(i+1,j+17)),
        lambda i,j:(Z(j),H(i,4),P(i,j+15),P(i+1,j+3)),
        lambda i,j:(Z(j),H(i,5),P(i,j+19),P(i+1,j+21)),
        lambda i,j:(Z(j),H(i,6),P(i,j+18),P(i+1,j+4)),
        lambda i,j:(Z(j),H(i,7),P(i,j+16),P(i+1,j+20)),
        lambda i,j:(Z(j),H(i,8),P(i,j+8),P(i+1,j+14)),
    ]
    for form in forms:
        for i in range(2):
            for j in range(22):
                blocks.append(form(i,j))
    return _norm(blocks)


def _normalise_special_vertex(blocks: Iterable[Sequence[int]], q: int, d: int) -> List[Tuple[int,...]]:
    """Relabel a q=3d+1 K4 cover so a degree-d vertex is local point 0.

    The other 3d points are arranged in d columns, one incident block per column,
    with local labels 1+layer*d+column.  This is the normalization used in Mills'
    Lemma 2 proof.
    """
    b = _norm(blocks)
    incidence: Dict[int,List[Block]] = {x:[] for x in range(1,q+1)}
    for B in b:
        for x in B:
            incidence[x].append(B)
    candidates = [x for x in range(1,q+1) if len(incidence[x]) == d]
    if not candidates:
        raise ValueError(f"no vertex of block-degree {d} in order-{q} cover")
    x0 = candidates[0]
    through = sorted(incidence[x0])
    mapping: Dict[int,int] = {x0:0}
    seen = set()
    for col,B in enumerate(through):
        others = sorted(x for x in B if x != x0)
        if len(others) != 3:
            raise AssertionError("bad incident K4")
        for layer,x in enumerate(others):
            if x in seen:
                raise AssertionError("chosen low-degree vertex has a repeated incident pair")
            seen.add(x)
            mapping[x] = 1 + layer*d + col
    if len(mapping) != q:
        raise AssertionError("incident blocks did not partition the remaining points")
    return sorted(tuple(sorted(mapping[x] for x in B)) for B in b)


def mills_lemma2(n: int, m: int) -> List[Block]:
    """Mills II, Lemma 2.

    Preconditions: m=7 or10 mod12, n=m or m+12 mod48, n>5m, and an optimum
    order-m cover is available.  The construction uses Mills' Lemma 1, realized
    as a truncated TD(5,w), and local optimum covers on 3|D|+1 points.
    """
    if m % 12 not in (7,10) or n % 48 not in (m % 48, (m + 12) % 48) or n <= 5*m:
        raise ValueError(f"Mills Lemma 2 conditions fail for n={n}, m={m}")
    u = (m - 1)//3
    t = (n - 1)//3
    if (t-u) % 4:
        raise AssertionError("nonintegral w in Mills Lemma 2")
    w = (t-u)//4
    if not (0 < u < w and w % 4 in (0,1)):
        raise ValueError(f"bad Lemma-2 parameters u={u}, w={w}")

    td = transversal.trans_with_groups(w, 5)
    mixed = transversal.truncate(td, u)
    Dsets: List[Tuple[int,...]] = [tuple(sorted(B)) for B in mixed]
    Dsets.extend(tuple(range(g*w+1,(g+1)*w+1)) for g in range(4))
    Dsets.append(tuple(range(4*w+1,4*w+u+1)))

    source_m = mills_k4_cover(m)
    cache: Dict[int,List[Tuple[int,...]]] = {}

    def local(d: int) -> List[Tuple[int,...]]:
        if d in cache:
            return cache[d]
        q = 3*d+1
        if q == m:
            src = source_m
        elif q % 12 in (1,4):
            from . import bibd4
            src = bibd4.bibd4(q)
        else:
            src = mills_k4_cover(q)
        cache[d] = _normalise_special_vertex(src,q,d)
        return cache[d]

    # Global labels: X=1 and (layer,j) -> 1+layer*t+j for layer=0,1,2,
    # j in T={1,...,t}.
    out = set()
    for D in Dsets:
        D = tuple(sorted(D))
        d = len(D)
        loc = local(d)
        for B in loc:
            mapped = []
            for x in B:
                if x == 0:
                    mapped.append(1)
                else:
                    z = x-1
                    layer = z//d
                    col = z%d
                    mapped.append(1 + layer*t + D[col])
            out.add(tuple(sorted(mapped)))
    blocks = sorted(out)
    return blocks


def mills_lemma3(n: int) -> List[Block]:
    """Mills II, Lemma 3, whenever the MacNeish TD(4,m) backend is available."""
    if n % 48 not in (10,46) or n <= 10:
        raise ValueError(f"Mills Lemma 3 does not apply to n={n}")
    m = (n-2)//4
    cross = transversal.trans_with_groups(m, 4)
    X,Y = 4*m+1,4*m+2
    blocks: List[Block] = [tuple(sorted(B)) for B in cross]
    from . import bibd4
    local = bibd4.bibd4(m+2)  # m+2 == 1 or4 mod12
    for g in range(4):
        points = [X,Y] + list(range(g*m+1,(g+1)*m+1))
        blocks.extend(_relabel_blocks(local, points))
    return _norm(blocks)


def mills_lemma4(n: int) -> List[Block]:
    """Mills II, Lemma 4 (Kirkman-schoolgirl lift).

    Write n=3m+1 with m=1 (mod 3).  A KTS(2m+1) has exactly m parallel
    classes.  Label these classes by the m points of an optimum order-m K4
    cover and adjoin the class label to every triple in that class.  Together
    with the order-m cover this gives an optimum order-n K4 cover.

    The finite KTS backend currently supplies exactly the four systems needed
    in Mills' proof: KTS(45), KTS(69), KTS(93), and KTS(141), yielding the
    previously exceptional orders 67, 103, 139, and 211.
    """
    if (n - 1) % 3:
        raise ValueError(f"Mills Lemma 4 needs n=3m+1, got n={n}")
    m = (n - 1)//3
    if m % 3 != 1:
        raise ValueError(f"Mills Lemma 4 needs m=1 (mod 3), got m={m}")
    from . import kirkman
    classes = kirkman.kirkman_triple_system(2*m + 1)
    if len(classes) != m:
        raise AssertionError("KTS has the wrong number of parallel classes")

    blocks: List[Block] = list(mills_k4_cover(m))
    # Core points are 1..m.  Schoolgirls occupy m+1..3m+1.
    for i, cls in enumerate(classes, start=1):
        for triple in cls:
            blocks.append(tuple(sorted((i, *(m + x for x in triple)))))
    return _norm(blocks)


def mills_construction_route(n: int) -> Tuple[str, ...]:
    """Return the deterministic construction route used for order ``n``.

    This is intentionally cheap: it checks only arithmetic and transversal
    capacities and does not materialise any blocks.  It is useful both for the
    dispatcher and for wide regression audits of the recursive spectrum.
    """
    if n % 12 in (1, 4):
        return ("bibd",)

    seeds = {
        22, 34, 70, 82,
        31, 43, 55, 79, 91, 115, 127, 151, 163, 199, 259,
    }
    if n in seeds:
        return ("seed",)

    if n in (67, 103, 139, 211):
        return ("lemma4",)

    if n in (58, 106, 154, 202):
        return ("lemma3",)
    if n % 48 == 46 and n > 10:
        # Here m=(n-2)/4 == 11 (mod 12), so all prime factors are >=5 and
        # MacNeish always supplies at least four groups.
        m = (n - 2) // 4
        if transversal.transversal_group_capacity(m) < 4:
            raise NotImplementedError(f"TD(4,{m}) route unexpectedly unavailable")
        return ("lemma3",)

    class10_sources = (22, 34, 46, 58, 70, 82, 94, 106)
    class7_sources = (31, 43, 55, 67, 79, 91, 103, 115, 127, 139, 151, 163, 199, 259)
    candidates = class10_sources if n % 12 == 10 else class7_sources if n % 12 == 7 else ()

    for m in candidates:
        if n <= 5 * m:
            continue
        if n % 48 not in (m % 48, (m + 12) % 48):
            continue
        u = (m - 1) // 3
        t = (n - 1) // 3
        if (t - u) % 4:
            continue
        w = (t - u) // 4
        if not (0 < u < w and w % 4 in (0, 1)):
            continue
        if transversal.transversal_group_capacity(w) < 5:
            continue
        return ("lemma2", str(m), str(w))

    raise NotImplementedError(f"Mills optimum K4 cover not yet implemented for n={n}")


def mills_k4_cover(n: int) -> List[Block]:
    """Return a deterministically constructed optimum K4 cover.

    The two Mills residue classes are dispatched through explicit finite seeds
    and Lemmas 2--4.  No exact-cover, SAT, ILP, or other search is used at run
    time.  :func:`mills_construction_route` performs the cheap route choice.
    """
    route = mills_construction_route(n)
    kind = route[0]

    if kind == "bibd":
        from . import bibd4
        return _norm(bibd4.bibd4(n))

    if kind == "seed":
        makers = {
            22:k4_seed22, 34:k4_seed34, 70:k4_seed70, 82:k4_seed82,
            31:k4_seed31, 43:k4_seed43, 55:k4_seed55, 79:k4_seed79, 91:k4_seed91,
            115:k4_seed115, 127:k4_seed127, 151:k4_seed151,
            163:k4_seed163, 199:k4_seed199, 259:k4_seed259,
        }
        return makers[n]()

    if kind == "lemma4":
        return mills_lemma4(n)

    if kind == "lemma3":
        return mills_lemma3(n)

    if kind == "lemma2":
        return mills_lemma2(n, int(route[1]))

    raise AssertionError(f"unknown Mills route {route}")


__all__ = [
    "mills_lower_bound", "analyse_k4_cover", "check_mills_cover",
    "mills_lemma2", "mills_lemma3", "mills_lemma4",
    "mills_construction_route", "mills_k4_cover",
    "k4_seed22", "k4_seed31", "k4_seed34", "k4_seed43", "k4_seed55",
    "k4_seed70", "k4_seed79", "k4_seed82", "k4_seed91", "k4_seed115",
    "k4_seed127", "k4_seed151", "k4_seed163", "k4_seed199", "k4_seed259",
]
