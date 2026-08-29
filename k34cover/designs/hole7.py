"""Construct PBD(v,{4,7*},1), equivalently a 7-hole 4-IPBD.

This module implements Brouwer's constructive proof for the spectrum
v == 7 or 10 (mod 12), v != 10,19.  Runtime construction is entirely
algebraic/design-theoretic: finite published starters, transversal designs,
Wilson-style weight-three inflation, and resolvable-design completion.
No exact-cover/SAT/ILP search is used.

The public function :func:`pbd_hole7` returns ``(external, hole)`` where
``external`` contains only 4-blocks and ``hole`` is the distinguished
7-block.  Thus ``external + [hole]`` is the PBD.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from itertools import combinations
from typing import Dict, Iterable, List, Sequence, Tuple

from . import bibd4, kirkman, mills, small, transversal
from . import resolvable

Block = Tuple[int, ...]
IPBD = Tuple[Tuple[Block, ...], Block]


def _norm(B: Sequence[int]) -> Block:
    return tuple(sorted(int(x) for x in B))


def _validate(v: int, external: Iterable[Sequence[int]], hole: Sequence[int]) -> None:
    """Strong checker for a (v,7;{4})-IPBD on points 1..v."""
    H = set(map(int, hole))
    if len(H) != 7 or min(H) < 1 or max(H) > v:
        raise AssertionError(f"order-{v} construction has an invalid 7-hole")
    mult: Counter[Tuple[int, int]] = Counter()
    blocks = []
    for raw in external:
        B = _norm(raw)
        if len(B) != 4 or len(set(B)) != 4 or B[0] < 1 or B[-1] > v:
            raise AssertionError(f"invalid external block in order-{v} 7-hole PBD: {raw}")
        if len(H.intersection(B)) > 1:
            raise AssertionError("external block contains two hole points")
        blocks.append(B)
        mult.update(combinations(B, 2))

    # Every pair not wholly in H occurs once; hole pairs occur zero times.
    expected = (v * (v - 1) // 2) - 21
    if len(mult) != expected or any(c != 1 for c in mult.values()):
        raise AssertionError(f"order-{v} 7-hole PBD pair property failed")
    for a, b in combinations(sorted(H), 2):
        if mult[(a, b)] != 0:
            raise AssertionError("a pair internal to the 7-hole was covered")


def _finish(v: int, external: Iterable[Sequence[int]], hole: Sequence[int]) -> IPBD:
    ext = tuple(sorted((_norm(B) for B in external)))
    H = _norm(hole)
    _validate(v, ext, H)
    return ext, H


def _split_full_pbd(v: int, blocks: Iterable[Sequence[int]]) -> IPBD:
    blocks = [_norm(B) for B in blocks]
    holes = [B for B in blocks if len(B) == 7]
    if len(holes) != 1 or any(len(B) not in (4, 7) for B in blocks):
        raise AssertionError(f"PBD({v}) does not have exactly one 7-block")
    H = holes[0]
    return _finish(v, [B for B in blocks if len(B) == 4], H)


def _map_ipbd(source: IPBD, ordinary: Sequence[int], hole: Sequence[int]) -> List[Block]:
    """Map only the external blocks of an IPBD onto ordinary+hole targets."""
    ext, src_hole = source
    src_h = set(src_hole)
    src_points = sorted({x for B in ext for x in B} | src_h)
    src_ord = [x for x in src_points if x not in src_h]
    if len(src_ord) != len(ordinary) or len(hole) != 7:
        raise AssertionError("IPBD relabelling has incompatible target sizes")
    mapping = {x: int(y) for x, y in zip(src_ord, ordinary)}
    mapping.update({x: int(y) for x, y in zip(src_hole, hole)})
    return [tuple(sorted(mapping[x] for x in B)) for B in ext]


def _gdd3_local(k: int) -> Sequence[Sequence[int]]:
    if k == 4:
        return bibd4.gdd4_3_4
    if k == 5:
        return bibd4.gdd4_3_5
    raise ValueError("weight-three inflation needs a master block of size 4 or 5")


def _inflate_blocks_by3(
    master_blocks: Iterable[Sequence[int]],
    copy_of: Dict[int, Tuple[int, int, int]],
) -> List[Block]:
    """Wilson FC: weight every master point by three."""
    out: List[Block] = []
    for raw in master_blocks:
        B = tuple(int(x) for x in raw)
        local = _gdd3_local(len(B))
        for C in local:
            mapped = []
            for x in C:
                g = (x - 1) // 3
                side = (x - 1) % 3
                mapped.append(copy_of[B[g]][side])
            out.append(tuple(sorted(mapped)))
    return out


# ---------------------------------------------------------------------------
# Brouwer's six finite base designs.


def _seed22() -> IPBD:
    ext, H = small.pbd22_hole7()
    return _finish(22, ext, H)


def _seed31() -> IPBD:
    """Brouwer, Theorem 3 proof, case A: complete seven triple factors."""
    def p(a: int, b: int, c: int) -> int:
        return 1 + 12 * (a % 2) + 6 * (b % 2) + (c % 6)

    def develop(block, das=(0,), dbs=(0,), dcs=(0,)):
        ans = []
        for da in das:
            for db in dbs:
                for dc in dcs:
                    ans.append(tuple(sorted(p(a+da, b+db, c+dc) for a,b,c in block)))
        return ans

    Q1=((0,0,0),(0,1,0),(1,0,0),(1,1,0))
    Q2=((0,0,0),(0,0,3),(1,1,1),(1,1,4))
    Q3=((0,0,0),(0,0,4),(1,1,5),(0,1,2))
    Q4=((0,0,1),(0,0,5),(1,1,2),(0,1,3))
    fours: List[Block] = []
    fours += develop(Q1, dcs=range(6))
    for Q in (Q2,Q3,Q4):
        fours += develop(Q, das=range(2), dbs=range(2))
    if len(set(fours)) != 18:
        raise AssertionError("Brouwer PBD31 quadruple starter developed incorrectly")

    F1=[
        ((0,0,0),(0,0,1),(0,0,2)),
        ((0,0,3),(0,0,4),(0,0,5)),
    ]
    F23=[
        ((0,0,0),(0,0,5),(0,1,1)),
        ((0,0,2),(1,1,0),(0,1,3)),
        ((1,1,1),(1,1,3),(1,0,4)),
        ((0,0,4),(1,1,2),(1,0,5)),
    ]
    F45=[
        ((0,0,2),(0,0,3),(1,0,4)),
        ((1,1,2),(1,1,5),(0,1,1)),
        ((0,0,0),(1,0,1),(0,1,4)),
        ((1,1,0),(1,0,3),(0,1,5)),
    ]
    F67=[
        ((0,0,0),(1,1,3),(0,1,5)),
        ((0,0,2),(0,0,4),(1,0,0)),
        ((0,0,1),(1,1,5),(1,0,4)),
        ((0,0,3),(1,1,2),(1,0,1)),
    ]

    classes: List[List[Block]] = []
    cls1=[]
    for T in F1:
        cls1 += develop(T, das=range(2), dbs=range(2))
    classes.append(sorted(set(cls1)))
    for starters in (F23,F45,F67):
        # Brouwer's notation first develops the bracket mod (-,2,-),
        # producing one factor, and then develops that *factor* mod
        # (2,-,-), producing its translate as the second factor.
        by_b=[]
        for T in starters:
            by_b += develop(T, dbs=range(2))
        by_b = sorted(set(by_b))
        classes.append(by_b)
        shifted=[]
        for T in by_b:
            pts=[]
            for x in T:
                z=x-1
                a=z//12; b=(z%12)//6; c=z%6
                pts.append(p(a+1,b,c))
            shifted.append(tuple(sorted(pts)))
        classes.append(sorted(shifted))
    if len(classes) != 7:
        raise AssertionError("Brouwer PBD31 has wrong number of triple factors")
    for cls in classes:
        if len(cls) != 8 or sorted(x for T in cls for x in T) != list(range(1,25)):
            raise AssertionError("Brouwer PBD31 triple factor is not a partition")

    H = tuple(range(25, 32))
    external = list(fours)
    for z, cls in zip(H, classes):
        external.extend(tuple(sorted((*T, z))) for T in cls)
    return _finish(31, external, H)


def _seed34() -> IPBD:
    return _split_full_pbd(34, kirkman.pbd34())


def _seed46() -> IPBD:
    """Shared Brouwer cyclic PBD(46,{4,7*}) finite ingredient."""
    ext, hole = small.pbd46_hole7()
    return _finish(46, ext, hole)


def _seed58() -> IPBD:
    """Brouwer cyclic PBD(58,{4,7*}) finite ingredient."""
    q = 17
    n = 58

    def P(i: int, j: int) -> int:
        return 1 + (i % 3) * q + (j % q)

    def H(a: int, i: int) -> int:
        return 3*q + 1 + (a % 2) * 3 + (i % 3)

    INF = n
    forms = (
        lambda i,j:(P(i,j),P(i,j+1),P(i,j+4),P(i+1,j+5)),
        lambda i,j:(P(i,j),P(i,j+2),P(i,j+8),P(i+1,j+11)),
        lambda i,j:(P(i,j),P(i,j+5),P(i+1,j+2),P(i+1,j+12)),
        lambda i,j:(P(i,j),P(i+1,j+8),P(i+2,j+7),H(0,i)),
        lambda i,j:(P(i,j),P(i+1,j+6),P(i+2,j+4),H(1,i)),
        lambda i,j:(P(0,j),P(1,j),P(2,j),INF),
    )
    blocks = set()
    for i in range(3):
        for j in range(q):
            for f in forms:
                blocks.add(tuple(sorted(f(i,j))))
    hole = tuple([H(a,i) for a in range(2) for i in range(3)] + [INF])
    return _finish(n, blocks, hole)


def _seed70() -> IPBD:
    """Recover Mills' B({4,22*};70) and fill its 22-block by the 7-hole PBD22."""
    all_blocks = mills.k4_seed70()
    big = set(range(1,23))
    cross = [B for B in all_blocks if not set(B).issubset(big)]
    ext22, H22 = _seed22()
    # The Mills 22-subset is already labelled 1..22.
    external = cross + list(ext22)
    return _finish(70, external, H22)


def _seed79() -> IPBD:
    """Recover Mills' B({4,13*,22*};79), then fill 13 and the 22-hole."""
    all_blocks = mills.k4_seed79()
    big22 = tuple(range(14,36))
    S22 = set(big22)
    cross_and_13 = [B for B in all_blocks if not set(B).issubset(S22)]
    ext22, H22 = _seed22()
    mapping = {i+1: big22[i] for i in range(22)}
    external = cross_and_13 + [tuple(sorted(mapping[x] for x in B)) for B in ext22]
    hole = tuple(mapping[x] for x in H22)
    return _finish(79, external, hole)


# ---------------------------------------------------------------------------
# General recursive constructions.


def _lemma6(v: int) -> IPBD:
    """Brouwer Lemma 6: v == 7 or 43 (mod 48), using TD(4,t)."""
    if v % 48 not in (7,43):
        raise ValueError("Lemma 6 residue condition failed")
    t = (v - 3) // 4
    td = transversal.trans_with_groups(t, 4)
    special = tuple(td[0])
    td_rest = [tuple(B) for B in td[1:]]
    extras = tuple(range(4*t + 1, 4*t + 4))
    external: List[Block] = [tuple(sorted(B)) for B in td_rest]

    local = list(bibd4.bibd4(t + 3))
    chosen = tuple(local[0])
    for g in range(4):
        group = list(range(g*t + 1, (g+1)*t + 1))
        a = special[g]
        prescribed = [a, *extras]
        src_chosen = list(chosen)
        mp = {src_chosen[i]: prescribed[i] for i in range(4)}
        src_rem = [x for x in range(1,t+4) if x not in mp]
        dst_rem = [x for x in group if x != a]
        if len(src_rem) != len(dst_rem):
            raise AssertionError("Lemma 6 local relabelling mismatch")
        mp.update(dict(zip(src_rem, dst_rem)))
        for B in local[1:]:
            external.append(tuple(sorted(mp[x] for x in B)))
    hole = tuple(sorted((*special, *extras)))
    return _finish(v, external, hole)


def _lemma2(u: int, t: int, h: int) -> IPBD:
    """Brouwer Lemma 2 in u=(v-7)/3 coordinates: u=4t+h."""
    if u != 4*t + h or not (0 <= h <= t):
        raise ValueError("invalid Lemma 2 parameters")
    source_t = _pbd_hole7_cached(3*t + 7)
    source_h = _pbd_hole7_cached(3*h + 7) if h else None

    td = transversal.trans_with_groups(t, 5)
    master = transversal.truncate(td, h)
    retained = list(range(1, 4*t + h + 1))
    copy_of = {x: (3*i+1,3*i+2,3*i+3) for i,x in enumerate(retained)}
    external = _inflate_blocks_by3(master, copy_of)

    groups: List[List[int]] = []
    for g in range(4):
        pts=[]
        for x in range(g*t+1,(g+1)*t+1):
            pts.extend(copy_of[x])
        groups.append(pts)
    if h:
        pts=[]
        for x in range(4*t+1,4*t+h+1):
            pts.extend(copy_of[x])
        groups.append(pts)

    v = 3*u + 7
    H = tuple(range(3*u + 1, 3*u + 8))
    for G in groups[:4]:
        external.extend(_map_ipbd(source_t, G, H))
    if h:
        assert source_h is not None
        external.extend(_map_ipbd(source_h, groups[4], H))
    return _finish(v, external, H)


def _seed94() -> IPBD:
    """Brouwer Lemma 7: complete a KTS(63), then fill its 31-block."""
    p31 = _seed31()
    full31 = list(p31[0]) + [p31[1]]
    classes = kirkman.kts_from_pbd(31, full31)  # KTS(63)
    new_points = list(range(64,95))
    external: List[Block] = []
    for z, cls in zip(new_points, classes):
        external.extend(tuple(sorted((*T,z))) for T in cls)
    # Fill the completed 31-block, keeping only its external 4-blocks.
    final_hole = tuple(new_points[-7:])
    ordinary = new_points[:-7]
    external.extend(_map_ipbd(p31, ordinary, final_hole))
    return _finish(94, external, final_hole)


def _lemma10(t: int, s: int) -> IPBD:
    """Brouwer Lemma 10 for the two exceptional targets 106 and 154."""
    n = 12*t + 4
    if (t,s) == (2,7):
        classes = resolvable.rbibd28()
    elif (t,s) == (3,11):
        classes = resolvable.rbibd40()
    else:
        raise NotImplementedError("only the two Brouwer Lemma-10 finite exceptions are needed")
    if not (1 <= s <= 4*t+1):
        raise ValueError("invalid partial-completion parameter")

    # Lemma 9: partially complete s parallel classes of RBIBD(n,4,1).
    infinities = list(range(n+1,n+s+1))
    master: List[Block] = []
    for j, cls in enumerate(classes):
        if j < s:
            z = infinities[j]
            master.extend(tuple(sorted((*B,z))) for B in cls)
        else:
            master.extend(tuple(B) for B in cls)
    distinguished = tuple(infinities)
    master_v = n+s

    # Lemma 10: weight every master point by 3, except that the distinguished
    # s-block is filled by an already constructed (3s+1,7)-IPBD.
    copy_of = {x:(3*(x-1)+1,3*(x-1)+2,3*(x-1)+3) for x in range(1,master_v+1)}
    external = _inflate_blocks_by3(master, copy_of)
    target_v = 3*master_v + 1
    omega = target_v

    inner = _pbd_hole7_cached(3*s + 1)
    inner_target = [y for x in distinguished for y in copy_of[x]] + [omega]
    # Make omega one of the seven final hole points.  Use six copies from the
    # distinguished master points for the rest of the hole.
    final_hole = tuple([omega] + [copy_of[x][0] for x in distinguished[:6]])
    target_ord = [x for x in inner_target if x not in set(final_hole)]
    external.extend(_map_ipbd(inner, target_ord, final_hole))

    # For each point outside the distinguished s-block add ({a}xZ_3)+omega.
    for a in range(1,n+1):
        external.append(tuple(sorted((*copy_of[a], omega))))
    return _finish(target_v, external, final_hole)


_BASE_U = {0,5,8,9,13,17,21,24,29,33,49}


def _lemma6_available_u(u: int) -> bool:
    v = 3*u + 7
    if v % 48 not in (7,43):
        return False
    t = (v - 3)//4
    try:
        return transversal.transversal_group_capacity(t) >= 4
    except Exception:
        return False


@lru_cache(maxsize=None)
def _can_u(u: int) -> bool:
    if u in _BASE_U:
        return True
    if u < 0 or u % 4 not in (0,1):
        return False
    if _lemma6_available_u(u):
        return True
    # Adaptive Brouwer Lemma 2.  The source parameters t,h are strictly
    # smaller than u, so this recursion terminates.  We deliberately choose a
    # route supported by the deterministic TD backend rather than assuming a
    # black-box MOLS existence oracle.
    for h in range(0, u//5 + 2):
        if h >= u:
            continue
        if h % 4 not in (0,1) or not _can_u(h):
            continue
        rem = u-h
        if rem % 4:
            continue
        t = rem//4
        if t < max(h,2) or not _can_u(t):
            continue
        try:
            if transversal.transversal_group_capacity(t) >= 5:
                return True
        except Exception:
            pass
    return False


@lru_cache(maxsize=None)
def _route_u(u: int):
    if u in _BASE_U:
        return ("base", u)
    if _lemma6_available_u(u):
        return ("lemma6",)
    for h in range(0, u//5 + 2):
        if h >= u:
            continue
        if h % 4 not in (0,1) or not _can_u(h):
            continue
        rem=u-h
        if rem%4:
            continue
        t=rem//4
        if t < max(h,2) or not _can_u(t):
            continue
        if transversal.transversal_group_capacity(t) >= 5:
            return ("lemma2",t,h)
    raise NotImplementedError(f"no deterministic Brouwer recursion route found for u={u}")


@lru_cache(maxsize=16)
def _pbd_hole7_cached(v: int) -> IPBD:
    if v == 7:
        return _finish(7, [], tuple(range(1,8)))
    if v in (10,19) or v < 7 or v % 12 not in (7,10):
        raise ValueError(f"PBD(v,{{4,7*}},1) is not admissible at v={v}")
    u=(v-7)//3
    route=_route_u(u)
    if route[0] == "base":
        makers={
            5:_seed22, 8:_seed31, 9:_seed34, 13:_seed46, 17:_seed58,
            21:_seed70, 24:_seed79, 29:_seed94,
            33:lambda:_lemma10(2,7), 49:lambda:_lemma10(3,11),
        }
        if u == 0:
            return _finish(7, [], tuple(range(1,8)))
        return makers[u]()
    if route[0] == "lemma6":
        return _lemma6(v)
    _,t,h=route
    return _lemma2(u,t,h)


def pbd_hole7(v: int) -> Tuple[List[Block], Block]:
    """Return the external K4 blocks and distinguished 7-hole at order ``v``."""
    ext,H=_pbd_hole7_cached(int(v))
    return list(ext), H


def pbd_hole7_full(v: int) -> List[Block]:
    """Return the complete PBD, including its unique 7-block."""
    ext,H=pbd_hole7(v)
    return sorted(ext+[H], key=lambda B:(len(B),B))


__all__=["pbd_hole7","pbd_hole7_full"]
