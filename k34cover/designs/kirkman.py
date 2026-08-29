"""Deterministic Kirkman triple systems used by the Mills/Brouwer recursions.

The runtime code contains no search.  The small KTS(9), KTS(15), and KTS(21)
are fixed finite designs.  Larger systems needed here are produced by the
standard PBD -> KTS construction: from a PBD(m) whose block sizes are 4 or 7,
place KTS(9) or KTS(15) on ``infinity + two copies`` of every PBD block and
splice the corresponding parallel classes.

Only the finite PBD ingredients required by this project are exposed:
orders 22, 34, 46 and 70.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from itertools import combinations
from typing import Iterable, List, Sequence, Tuple

Block = Tuple[int, ...]
ParallelClass = Tuple[Block, ...]


def _norm_block(raw: Sequence[int]) -> Block:
    return tuple(sorted(int(x) for x in raw))


def _verify_kts(v: int, classes: Sequence[Sequence[Sequence[int]]]) -> None:
    if v % 6 != 3:
        raise AssertionError(f"KTS order {v} is inadmissible")
    if len(classes) != (v - 1) // 2:
        raise AssertionError(f"KTS({v}) has the wrong number of parallel classes")
    mult: Counter[Tuple[int, int]] = Counter()
    seen = set()
    for cls in classes:
        flat = [int(x) for B in cls for x in B]
        if sorted(flat) != list(range(1, v + 1)):
            raise AssertionError(f"a KTS({v}) class is not a partition")
        if len(cls) != v // 3:
            raise AssertionError(f"a KTS({v}) class has the wrong size")
        for raw in cls:
            B = _norm_block(raw)
            if len(B) != 3 or len(set(B)) != 3:
                raise AssertionError("invalid KTS triple")
            if B in seen:
                raise AssertionError("repeated KTS triple")
            seen.add(B)
            mult.update(combinations(B, 2))
    if len(seen) != v * (v - 1) // 6:
        raise AssertionError(f"KTS({v}) has the wrong number of triples")
    if len(mult) != v * (v - 1) // 2 or any(c != 1 for c in mult.values()):
        raise AssertionError(f"KTS({v}) pair property failed")


def _verify_pbd(v: int, blocks: Iterable[Sequence[int]], sizes=(4, 7)) -> List[Block]:
    out = [_norm_block(B) for B in blocks]
    mult: Counter[Tuple[int, int]] = Counter()
    for B in out:
        if len(B) not in sizes or len(set(B)) != len(B):
            raise AssertionError(f"invalid PBD({v}) block {B}")
        if B[0] < 1 or B[-1] > v:
            raise AssertionError(f"PBD({v}) point out of range")
        mult.update(combinations(B, 2))
    if len(mult) != v * (v - 1) // 2 or any(c != 1 for c in mult.values()):
        raise AssertionError(f"PBD({v}) pair property failed")
    return sorted(out, key=lambda B: (len(B), B))


@lru_cache(maxsize=1)
def _kts9() -> Tuple[ParallelClass, ...]:
    # Lindner--Rodger, Design Theory, Example 5.1.1.
    classes = (
        ((1,2,3),(4,5,6),(7,8,9)),
        ((1,4,7),(2,5,8),(3,6,9)),
        ((1,5,9),(2,6,7),(3,4,8)),
        ((1,6,8),(2,4,9),(3,5,7)),
    )
    out = tuple(tuple(_norm_block(B) for B in cls) for cls in classes)
    _verify_kts(9, out)
    return out


@lru_cache(maxsize=1)
def _kts15() -> Tuple[ParallelClass, ...]:
    # Lindner--Rodger, Design Theory, Example 5.1.1.
    classes = (
        ((1,2,3),(4,8,12),(5,10,14),(6,11,13),(7,9,15)),
        ((1,4,5),(2,8,10),(3,13,15),(6,9,14),(7,11,12)),
        ((1,6,7),(2,9,11),(3,12,14),(4,10,15),(5,8,13)),
        ((1,8,9),(2,12,15),(3,5,6),(4,11,14),(7,10,13)),
        ((1,10,11),(2,13,14),(3,4,7),(5,9,12),(6,8,15)),
        ((1,12,13),(2,4,6),(3,9,10),(5,11,15),(7,8,14)),
        ((1,14,15),(2,5,7),(3,8,11),(4,9,13),(6,10,12)),
    )
    out = tuple(tuple(_norm_block(B) for B in cls) for cls in classes)
    _verify_kts(15, out)
    return out


@lru_cache(maxsize=1)
def _kts21() -> Tuple[ParallelClass, ...]:
    """A fixed KTS(21) finite ingredient.

    The underlying STS is the standard GF(7) pure/mixed-difference system;
    the displayed resolution is fixed once and for all, so no resolution
    search occurs at runtime.
    """
    rows = (
        ((1,8,15),(2,9,16),(3,10,17),(4,11,18),(5,12,19),(6,13,20),(7,14,21)),
        ((1,9,20),(2,3,7),(4,8,17),(5,11,16),(6,14,18),(10,12,13),(15,19,21)),
        ((1,14,19),(2,4,5),(3,9,21),(6,12,17),(7,13,18),(8,10,11),(15,16,20)),
        ((1,5,7),(2,10,21),(3,8,18),(4,12,16),(6,9,15),(11,13,14),(17,19,20)),
        ((1,13,16),(2,12,18),(3,11,15),(4,14,20),(5,8,21),(6,10,19),(7,9,17)),
        ((1,10,18),(2,11,19),(3,12,20),(4,6,7),(5,14,15),(8,9,13),(16,17,21)),
        ((1,3,4),(2,8,20),(5,13,17),(6,11,21),(7,12,15),(9,10,14),(16,18,19)),
        ((1,2,6),(3,14,16),(4,13,21),(5,10,20),(7,8,19),(9,11,12),(15,17,18)),
        ((1,12,21),(2,14,17),(3,13,19),(4,10,15),(5,9,18),(6,8,16),(7,11,20)),
        ((1,11,17),(2,13,15),(3,5,6),(4,9,19),(7,10,16),(8,12,14),(18,20,21)),
    )
    out = tuple(tuple(_norm_block(B) for B in cls) for cls in rows)
    _verify_kts(21, out)
    return out


def _local_model(k: int) -> Tuple[ParallelClass, ...]:
    if k == 4:
        return _kts9()
    if k == 7:
        return _kts15()
    raise ValueError(f"PBD->KTS local block size {k} is unsupported")


def _mapped_local_kts(base_block: Sequence[int]) -> Tuple[Tuple[ParallelClass, ...], dict[int, int]]:
    """Map a local KTS(2k+1) to infinity + two copies of ``base_block``.

    Local point 1 is infinity.  In both fixed local systems, every parallel
    class has a unique triple through 1.  The other two points of those
    triples form k disjoint pairs, which are mapped to the two copies of the
    corresponding PBD point.  The returned dictionary maps each base point to
    the index of the local parallel class containing its vertical triple.
    """
    B = tuple(sorted(map(int, base_block)))
    model = _local_model(len(B))
    pair_by_class: List[Tuple[int, int]] = []
    for cls in model:
        through = [T for T in cls if 1 in T]
        if len(through) != 1:
            raise AssertionError("local KTS class does not have one infinity triple")
        pair = tuple(sorted(x for x in through[0] if x != 1))
        pair_by_class.append(pair)  # type: ignore[arg-type]
    flat = [x for p in pair_by_class for x in p]
    if sorted(flat) != list(range(2, 2*len(B)+2)):
        raise AssertionError("local infinity triples do not partition finite points")

    # Temporary target labels: infinity=0; copies of x are 2*x-1 and 2*x.
    mp = {1: 0}
    class_of: dict[int, int] = {}
    for ci, (x, pair) in enumerate(zip(B, pair_by_class)):
        mp[pair[0]] = 2*x - 1
        mp[pair[1]] = 2*x
        class_of[x] = ci
    mapped = tuple(
        tuple(tuple(sorted(mp[z] for z in T)) for T in cls)
        for cls in model
    )
    return mapped, class_of


def kts_from_pbd(m: int, blocks: Iterable[Sequence[int]]) -> Tuple[ParallelClass, ...]:
    """Construct KTS(2m+1) from a PBD(m) with block sizes 4 and 7.

    This is the standard recursive construction in which target point 1 is
    infinity and base point x has copies ``2*x`` and ``2*x+1``.
    """
    m = int(m)
    pbd = _verify_pbd(m, blocks)
    if (2*m + 1) % 6 != 3:
        raise ValueError(f"PBD order {m} does not lead to an admissible KTS")

    INF = 1
    def copy(x: int, side: int) -> int:
        return 2*x + side  # side 0,1 -> 2x,2x+1; range 2..2m+1

    # Local data, one entry per PBD block.
    local_data = []
    blocks_through = {x: [] for x in range(1, m+1)}
    for bi, B in enumerate(pbd):
        mapped, class_of = _mapped_local_kts(B)
        local_data.append((B, mapped, class_of))
        for x in B:
            blocks_through[x].append(bi)

    classes: List[ParallelClass] = []
    for x in range(1, m+1):
        vertical = tuple(sorted((INF, copy(x,0), copy(x,1))))
        cls: List[Block] = [vertical]
        for bi in blocks_through[x]:
            B, mapped, class_of = local_data[bi]
            lci = class_of[x]
            local_cls = mapped[lci]
            # Translate temporary local labels 0 and (2*y-1,2*y) to the
            # global infinity/copy labels.  Temporary labels encode y itself.
            for T in local_cls:
                if 0 in T:
                    # This is the vertical triple for x; globally include it once.
                    continue
                glob = []
                for z in T:
                    if z == 0:
                        glob.append(INF)
                    else:
                        y = (z + 1)//2
                        side = 0 if z % 2 == 1 else 1
                        glob.append(copy(y, side))
                cls.append(tuple(sorted(glob)))
        classes.append(tuple(sorted(cls)))

    out = tuple(classes)
    _verify_kts(2*m+1, out)
    return out


@lru_cache(maxsize=1)
def _pbd22() -> Tuple[Block, ...]:
    """Shared primitive PBD(22,{4,7*}) finite ingredient."""
    from . import small
    external, hole = small.pbd22_hole7()
    return tuple(_verify_pbd(22, list(external) + [hole]))


@lru_cache(maxsize=1)
def pbd34() -> Tuple[Block, ...]:
    """Brouwer's PBD(34,{4,7*}) on Z_9 x Z_3 plus seven points."""
    q = 9
    def P(i: int, j: int) -> int:
        return 1 + (j % 3)*q + (i % q)

    blocks: List[Block] = []
    factors: List[List[Block]] = [[] for _ in range(7)]
    for i in range(9):
        for j in range(3):
            blocks.append(tuple(sorted((P(i,j),P(i+2,j+1),P(i+2,j+2),P(i+3,j+2)))))
            T2 = tuple(sorted((P(i,j),P(i+3,j+1),P(i+5,j+1))))
            factors[(i % 3 + 2*j) % 3].append(T2)
            T3 = tuple(sorted((P(i,j),P(i+4,j+1),P(i+8,j+1))))
            factors[3 + i % 3].append(T3)
    for j in range(3):
        for i in range(3):
            factors[6].append(tuple(sorted((P(i,j),P(i+3,j),P(i+6,j)))))
    for F in factors:
        if len(F) != 9 or sorted(x for T in F for x in T) != list(range(1,28)):
            raise AssertionError("PBD34 triple factor failed")
    for z, F in zip(range(28,35), factors):
        blocks.extend(tuple(sorted((*T,z))) for T in F)
    blocks.append(tuple(range(28,35)))
    return tuple(_verify_pbd(34, blocks))


@lru_cache(maxsize=1)
def _pbd46() -> Tuple[Block, ...]:
    """Shared Brouwer cyclic PBD(46,{4,7*}) finite ingredient."""
    from . import small
    external, hole = small.pbd46_hole7()
    return tuple(_verify_pbd(46, list(external) + [hole]))


@lru_cache(maxsize=1)
def _pbd70() -> Tuple[Block, ...]:
    """PBD(70,{4,7*}) by filling Mills' distinguished 22-set with PBD22."""
    from . import mills
    all_blocks = mills.k4_seed70()
    big = set(range(1,23))
    cross = [B for B in all_blocks if not set(B).issubset(big)]
    # Fill the 22-set by our PBD22 (whose labels already are 1..22).
    blocks = cross + list(_pbd22())
    return tuple(_verify_pbd(70, blocks))


def pbd_for_kirkman(m: int) -> List[Block]:
    """Return the finite PBD(m,{4,7}) used to build the required KTS."""
    m = int(m)
    if m == 22:
        return list(_pbd22())
    if m == 34:
        return list(pbd34())
    if m == 46:
        return list(_pbd46())
    if m == 70:
        return list(_pbd70())
    raise NotImplementedError(f"no finite PBD-for-Kirkman ingredient registered at m={m}")


@lru_cache(maxsize=None)
def _kts_cached(v: int) -> Tuple[ParallelClass, ...]:
    if v == 9:
        return _kts9()
    if v == 15:
        return _kts15()
    if v == 21:
        return _kts21()
    m = (v - 1)//2
    if v in (45,69,93,141):
        return kts_from_pbd(m, pbd_for_kirkman(m))
    raise NotImplementedError(f"no deterministic KTS({v}) ingredient is registered")


def kirkman_triple_system(v: int) -> Tuple[ParallelClass, ...]:
    """Return the deterministic KTS needed by the covering recursions."""
    return _kts_cached(int(v))


__all__ = ["kirkman_triple_system", "kts_from_pbd", "pbd_for_kirkman", "pbd34"]
