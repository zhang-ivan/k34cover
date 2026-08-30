"""Transversal-design primitives used by the recursive constructions.

The original project constructed TD(q+1,q) by first constructing PG(2,q), using
third-party ``galois`` and ``primefac`` packages.  For the covering code we only
need the transversal design itself.  It has a much smaller direct finite-field
construction, implemented here with elementary polynomial arithmetic over GF(p).
The small number-theory operations needed by that construction are implemented
locally, so the active generator has no third-party runtime dependency while
preserving the old public API.
"""

from __future__ import annotations

import itertools
import math
from collections import Counter
from functools import lru_cache
from typing import Dict, Iterable, List, Sequence, Tuple

from k34cover._number_theory import factorint, is_irreducible_monic, is_prime

Block = Tuple[int, ...]


def _digits(a: int, p: int, degree: int) -> List[int]:
    out = []
    for _ in range(degree):
        out.append(a % p)
        a //= p
    return out


def _from_digits(coeffs: Sequence[int], p: int) -> int:
    value = 0
    place = 1
    for c in coeffs:
        value += (c % p) * place
        place *= p
    return value


@lru_cache(maxsize=None)
def _irreducible_modulus(p: int, degree: int) -> Tuple[int, ...]:
    """Return low-to-high coefficients of a monic irreducible degree-d polynomial."""
    if degree == 1:
        return (0, 1)
    if not is_prime(p):
        raise ValueError(f"p={p} is not prime")
    # A reducible monic polynomial of degree >1 with zero constant term is
    # divisible by x, so restrict to nonzero constants.
    for c0 in range(1, p):
        for rest in itertools.product(range(p), repeat=degree - 1):
            coeffs = (c0, *rest, 1)
            if is_irreducible_monic(coeffs, p):
                return tuple(int(c) for c in coeffs)
    raise RuntimeError(f"could not find irreducible polynomial over GF({p}) of degree {degree}")


def _gf_add(a: int, b: int, p: int, degree: int) -> int:
    if degree == 1:
        return (a + b) % p
    da = _digits(a, p, degree)
    db = _digits(b, p, degree)
    return _from_digits([(x + y) % p for x, y in zip(da, db)], p)


def _gf_mul(a: int, b: int, p: int, degree: int) -> int:
    if degree == 1:
        return (a * b) % p
    if a == 0 or b == 0:
        return 0
    da = _digits(a, p, degree)
    db = _digits(b, p, degree)
    prod = [0] * (2 * degree - 1)
    for i, x in enumerate(da):
        for j, y in enumerate(db):
            prod[i + j] = (prod[i + j] + x * y) % p

    modulus = _irreducible_modulus(p, degree)  # low-to-high, monic
    for k in range(len(prod) - 1, degree - 1, -1):
        c = prod[k] % p
        if not c:
            continue
        shift = k - degree
        # subtract c*x^shift*f(x)
        for j in range(degree):
            prod[shift + j] = (prod[shift + j] - c * modulus[j]) % p
        prod[k] = 0
    return _from_digits(prod[:degree], p)


def trans1(p: int, alpha: int, blocks=None, groups=None) -> List[Block]:
    """Generate TD(q+1,q), q=p**alpha (old ``Lemma 3.5`` API).

    For each x,y in GF(q), use the block
        (x, y, x+a*y for every nonzero a in GF(q)),
    with each coordinate placed in its own group.  Any two coordinates determine
    x and y uniquely, hence every cross-group pair occurs exactly once.
    """
    del groups  # kept only for backward call compatibility
    if not is_prime(p):
        raise ValueError(f"p={p} is not prime")
    if alpha < 1:
        raise ValueError("alpha must be positive")
    q = p**alpha
    out: List[Block] = [] if blocks is None else list(blocks)
    nonzero = list(range(1, q))
    for x in range(q):
        for y in range(q):
            coords = [x, y]
            coords.extend(_gf_add(x, _gf_mul(a, y, p, alpha), p, alpha) for a in nonzero)
            block = tuple(group * q + value + 1 for group, value in enumerate(coords))
            out.append(block)
    return sorted(out)


def trans_trim(blocks: Iterable[Sequence[int]], t: int = 5) -> List[Block]:
    """Trim TD(s,r) to TD(t,r), t<=s."""
    return [tuple(block[:t]) for block in blocks]


def trans_mult(blocks_1: Iterable[Sequence[int]], blocks_2: Iterable[Sequence[int]], blocks=None) -> List[Block]:
    """Multiplication TD(s,r1) x TD(s,r2) -> TD(s,r1*r2)."""
    b1 = list(blocks_1)
    b2 = list(blocks_2)
    if not b1 or not b2:
        return []
    out = [] if blocks is None else list(blocks)
    r2 = math.isqrt(len(b2))
    if r2 * r2 != len(b2):
        raise ValueError("second transversal design does not have r^2 blocks")
    for block_1 in b1:
        for block_2 in b2:
            block_tmp = []
            for x in block_2:
                group = (x - 1) // r2
                within = (x - 1) % r2
                value = (block_1[group] - 1) * r2 + within + 1
                block_tmp.append(value)
            out.append(tuple(block_tmp))
    return sorted(out)


def prime_factor_mult(n: int) -> Dict[int, int]:
    """Prime factorization as ``{prime: exponent}``."""
    if n < 2:
        raise ValueError("n must be at least 2")
    return dict(factorint(n))


def trans2(r: int) -> List[Block]:
    """Construct TD(s,r), s=1+min(p_i**a_i), by the MacNeish product."""
    factors_dict = prime_factor_mult(r)
    min_factor = min(factors_dict, key=lambda factor: factor ** factors_dict[factor])
    s = min_factor ** factors_dict[min_factor] + 1
    blocks = trans1(min_factor, factors_dict[min_factor])
    del factors_dict[min_factor]
    for prime, exponent in list(factors_dict.items()):
        blocks_tmp = trans_trim(trans1(prime, exponent), s)
        blocks = trans_mult(blocks, blocks_tmp)
    return blocks



@lru_cache(maxsize=1)
def _trans_bck12() -> Tuple[Block, ...]:
    """Return the explicit TD(7,12) of Bose--Chakravarti--Knuth.

    The 1960 Technometrics paper *On Methods of Constructing Sets of Mutually
    Orthogonal Latin Squares Using a Computer. I*, Figure 1, gives five MOLS
    of order 12.  Row, column, and their five entries are the seven groups of
    a TD(7,12).  Keeping this one finite ingredient explicit lets Mills'
    three-MOLS recursion pass through the otherwise MacNeish-exceptional
    parameter 12, without doing any run-time search.
    """
    squares = (
        (
            (1,2,3,4,5,6,7,8,9,10,11,12),
            (2,3,4,5,6,1,8,9,10,11,12,7),
            (3,4,5,6,1,2,9,10,11,12,7,8),
            (4,5,6,1,2,3,10,11,12,7,8,9),
            (5,6,1,2,3,4,11,12,7,8,9,10),
            (6,1,2,3,4,5,12,7,8,9,10,11),
            (7,8,9,10,11,12,1,2,3,4,5,6),
            (8,9,10,11,12,7,2,3,4,5,6,1),
            (9,10,11,12,7,8,3,4,5,6,1,2),
            (10,11,12,7,8,9,4,5,6,1,2,3),
            (11,12,7,8,9,10,5,6,1,2,3,4),
            (12,7,8,9,10,11,6,1,2,3,4,5),
        ),
        (
            (1,2,3,4,5,6,7,8,9,10,11,12),
            (3,4,5,6,1,2,9,10,11,12,7,8),
            (2,3,4,5,6,1,8,9,10,11,12,7),
            (11,12,7,8,9,10,5,6,1,2,3,4),
            (10,11,12,7,8,9,4,5,6,1,2,3),
            (12,7,8,9,10,11,6,1,2,3,4,5),
            (4,5,6,1,2,3,10,11,12,7,8,9),
            (6,1,2,3,4,5,12,7,8,9,10,11),
            (5,6,1,2,3,4,11,12,7,8,9,10),
            (8,9,10,11,12,7,2,3,4,5,6,1),
            (7,8,9,10,11,12,1,2,3,4,5,6),
            (9,10,11,12,7,8,3,4,5,6,1,2),
        ),
        (
            (1,2,3,4,5,6,7,8,9,10,11,12),
            (11,12,7,8,9,10,5,6,1,2,3,4),
            (5,6,1,2,3,4,11,12,7,8,9,10),
            (9,10,11,12,7,8,3,4,5,6,1,2),
            (3,4,5,6,1,2,9,10,11,12,7,8),
            (7,8,9,10,11,12,1,2,3,4,5,6),
            (10,11,12,7,8,9,4,5,6,1,2,3),
            (2,3,4,5,6,1,8,9,10,11,12,7),
            (8,9,10,11,12,7,2,3,4,5,6,1),
            (6,1,2,3,4,5,12,7,8,9,10,11),
            (12,7,8,9,10,11,6,1,2,3,4,5),
            (4,5,6,1,2,3,10,11,12,7,8,9),
        ),
        (
            (1,2,3,4,5,6,7,8,9,10,11,12),
            (6,1,2,3,4,5,12,7,8,9,10,11),
            (10,11,12,7,8,9,4,5,6,1,2,3),
            (3,4,5,6,1,2,9,10,11,12,7,8),
            (11,12,7,8,9,10,5,6,1,2,3,4),
            (8,9,10,11,12,7,2,3,4,5,6,1),
            (9,10,11,12,7,8,3,4,5,6,1,2),
            (5,6,1,2,3,4,11,12,7,8,9,10),
            (12,7,8,9,10,11,6,1,2,3,4,5),
            (2,3,4,5,6,1,8,9,10,11,12,7),
            (4,5,6,1,2,3,10,11,12,7,8,9),
            (7,8,9,10,11,12,1,2,3,4,5,6),
        ),
        (
            (1,2,3,4,5,6,7,8,9,10,11,12),
            (7,8,9,10,11,12,1,2,3,4,5,6),
            (6,1,2,3,4,5,12,7,8,9,10,11),
            (8,9,10,11,12,7,2,3,4,5,6,1),
            (12,7,8,9,10,11,6,1,2,3,4,5),
            (5,6,1,2,3,4,11,12,7,8,9,10),
            (3,4,5,6,1,2,9,10,11,12,7,8),
            (9,10,11,12,7,8,3,4,5,6,1,2),
            (11,12,7,8,9,10,5,6,1,2,3,4),
            (4,5,6,1,2,3,10,11,12,7,8,9),
            (2,3,4,5,6,1,8,9,10,11,12,7),
            (10,11,12,7,8,9,4,5,6,1,2,3),
        ),
    )
    out = []
    q = 12
    for row in range(q):
        for col in range(q):
            values = [row + 1, col + 1] + [L[row][col] for L in squares]
            out.append(tuple(g*q + value for g, value in enumerate(values)))
    return tuple(sorted(out))




def _verify_td(blocks: Sequence[Sequence[int]], r: int, groups: int) -> None:
    """Strong internal checker for a finite TD(groups,r) ingredient."""
    from collections import Counter
    if len(blocks) != r*r or any(len(B) != groups for B in blocks):
        raise AssertionError(f"TD({groups},{r}) has wrong size")
    mult = Counter()
    for B in blocks:
        seen_groups = set()
        for x in B:
            g = (x-1)//r
            if g in seen_groups or not 0 <= g < groups:
                raise AssertionError(f"TD({groups},{r}) block repeats a group")
            seen_groups.add(g)
        for x,y in itertools.combinations(B,2):
            mult[tuple(sorted((x,y)))] += 1
    if len(mult) != math.comb(groups,2)*r*r or any(c != 1 for c in mult.values()):
        raise AssertionError(f"TD({groups},{r}) pair property failed")


def _distinct_cross_quadruples(k: int) -> List[Tuple[int,...]]:
    """Four-group blocks covering exactly the pairs with unequal symbols.

    A TD(5,k) has a parallel class given by any fixed value in its fifth
    coordinate.  Normalise one such class to the k diagonal blocks and remove
    it; projecting to the first four groups leaves k(k-1) quadruples, exactly
    Mills I, Lemma 5.
    """
    td = trans_with_groups(k,5)
    cols = [tuple((x-1)%k for x in B) for B in td]
    fibre = [C for C in cols if C[4] == 0]
    if len(fibre) != k:
        raise AssertionError("TD(5,k) fibre has wrong size")
    fibre.sort(key=lambda C:C[0])
    perms: List[Dict[int,int]] = []
    for row in range(4):
        pmap = {C[row]:C[0] for C in fibre}
        if len(pmap) != k:
            raise AssertionError("failed to normalise TD(5,k) fibre")
        perms.append(pmap)
    out=[]
    for C in cols:
        norm=tuple(perms[row][C[row]] for row in range(4))
        if C[4] == 0:
            if len(set(norm)) != 1:
                raise AssertionError("removed fibre is not diagonal")
            continue
        out.append(tuple(row*k + norm[row] + 1 for row in range(4)))
    if len(out) != k*(k-1):
        raise AssertionError("distinct-cross ingredient has wrong size")
    return out


@lru_cache(maxsize=1)
def _trans_mills10() -> Tuple[Block, ...]:
    """Mills I, p.74: explicit TD(4,10) extending a TD(4,3)."""
    # Klein four group, represented by two bits.
    R=[(0,0),(1,0),(0,1),(1,1)]
    ridx={x:i for i,x in enumerate(R)}
    add=lambda x,y:((x[0]^y[0]),(x[1]^y[1]))
    q=10
    def Z(g:int,t:int)->int:
        return g*q + (t%7) + 1
    def U(g:int,i:int)->int:
        return g*q + 8 + i  # i=0,1,2

    out:List[Block]=[]
    for t in range(7):
        out.append(tuple(Z(g,t) for g in range(4)))
    # Mills writes r+r_1,...,r+r_4; take r_1,...,r_4 to be all of V_4.
    for r in R:
        for t in range(7):
            for i in range(1,4):
                gs=[ridx[add(r,x)] for x in R]
                out.append((Z(gs[0],t), Z(gs[1],t+i), Z(gs[2],t-i), U(gs[3],i-1)))

    # Fill the 3-point hole by TD(4,3).
    for B in trans_trim(trans1(3,1),4):
        out.append(tuple(U((x-1)//3,(x-1)%3) for x in B))
    out=sorted(tuple(sorted(B)) for B in out)
    _verify_td(out,10,4)
    return tuple(out)



@lru_cache(maxsize=1)
def _trans_bsp26() -> Tuple[Block, ...]:
    """Bose--Shrikhande--Parker Example 12: explicit TD(4,26).

    The 1960 Canadian J. Math. paper gives a 4x7 starter P0 over Z_23
    together with three indefinites x1,x2,x3.  Cyclically permuting its rows,
    developing the ring entries by all 23 translations, and adjoining the
    23 constant ring columns plus OA(9,4,3,2) on the indefinites produces
    OA(26^2,4,26,2), hence a pair of orthogonal Latin squares of order 26.
    """
    X1,X2,X3=23,24,25
    P0=(
        (0,0,0,0,X1,X2,X3),
        (3,6,2,1,0,0,0),
        (8,20,12,16,20,17,8),
        (12,16,7,2,19,6,21),
    )
    # A0=[P0,P1,P2,P3], where P_i are cyclic row permutations of P0.
    starter_cols:List[Tuple[int,...]]=[]
    for shift in range(4):
        rows=P0[shift:]+P0[:shift]
        for j in range(7):
            starter_cols.append(tuple(rows[r][j] for r in range(4)))

    cols:List[Tuple[int,...]]=[]
    for theta in range(23):
        for C in starter_cols:
            cols.append(tuple(((x+theta)%23 if x<23 else x) for x in C))
    # Equal ring-symbol pairs.
    cols.extend((x,x,x,x) for x in range(23))
    # All pairs among the three indefinites.
    for B in trans_trim(trans1(3,1),4):
        vals=tuple(X1 + ((x-1)%3) for x in B)
        cols.append(vals)
    if len(cols)!=26*26:
        raise AssertionError("BSP OA(4,26) has wrong number of columns")
    out=[tuple(r*26+C[r]+1 for r in range(4)) for C in cols]
    out=sorted(tuple(sorted(B)) for B in out)
    _verify_td(out,26,4)
    return tuple(out)

@lru_cache(maxsize=1)
def _trans_mills38() -> Tuple[Block, ...]:
    """Mills I, p.75: deterministic TD(4,38) via the cyclic 5-BIBD(41)."""
    # Bose's cyclic 2-(41,5,1) design quoted by Mills.
    bibd=[]
    starters=((0,9,15,17,36),(0,3,4,16,34))
    for w in range(41):
        for S0 in starters:
            bibd.append(tuple(sorted((w+x)%41 for x in S0)))
    from collections import Counter
    check=Counter()
    for B in bibd: check.update(itertools.combinations(B,2))
    if len(check)!=math.comb(41,2) or any(c!=1 for c in check.values()):
        raise AssertionError("cyclic BIBD(41,5,1) verification failed")

    deleted={0,1,2}
    if any(deleted.issubset(B) for B in bibd):
        raise AssertionError("chosen deleted points lie in one quintuple")
    remain=sorted(set(range(41))-deleted)
    pos={x:i for i,x in enumerate(remain)}
    pbd=[]
    for B in bibd:
        C=tuple(sorted(pos[x] for x in B if x not in deleted))
        if len(C)>=2:
            pbd.append(C)
    triples=sorted(B for B in pbd if len(B)==3)
    quads=[B for B in pbd if len(B)==4]
    quints=[B for B in pbd if len(B)==5]
    if len(triples)!=3 or any(len(set(A)&set(B)) for A,B in itertools.combinations(triples,2)):
        raise AssertionError("Mills 38-point truncation did not yield three disjoint triples")
    U,C1,C2=triples

    local3=trans_trim(trans1(3,1),4)
    local4=_distinct_cross_quadruples(4)
    local5=_distinct_cross_quadruples(5)
    out:List[Block]=[]
    def map_local(local:Iterable[Sequence[int]], D:Sequence[int], k:int)->None:
        for B in local:
            mapped=[]
            for x in B:
                g=(x-1)//k; z=(x-1)%k
                mapped.append(g*38 + D[z] + 1)
            out.append(tuple(mapped))
    map_local(local3,C1,3); map_local(local3,C2,3)
    for D in quads: map_local(local4,D,4)
    for D in quints: map_local(local5,D,5)
    special=set(U)|set(C1)|set(C2)
    for t in range(38):
        if t not in special:
            out.append(tuple(g*38+t+1 for g in range(4)))
    # Fill the remaining 3-point hole U.
    map_local(local3,U,3)
    out=sorted(tuple(sorted(B)) for B in out)
    _verify_td(out,38,4)
    return tuple(out)


@lru_cache(maxsize=1)
def _trans_mills50() -> Tuple[Block, ...]:
    """Mills I, pp.75--76: extend TD(4,10) to TD(4,50)."""
    td10=list(_trans_mills10())
    out:List[Block]=[]
    # Global point in group r is indexed by (a,b) in Z_5 x B_10.
    def P(r:int,a:int,b:int)->int:
        return r*50 + (a%5)*10 + (b%10) + 1
    for a1 in range(5):
        for a2 in range(5):
            if a1==0 and a2==0:
                continue
            for B in td10:
                mapped=[]
                for x in B:
                    r=(x-1)//10; b=(x-1)%10
                    mapped.append(P(r,a1+r*a2,b))
                out.append(tuple(mapped))
    # Fill the omitted U={(0,b): b in B_10}.
    for B in td10:
        out.append(tuple(P((x-1)//10,0,(x-1)%10) for x in B))
    out=sorted(tuple(sorted(B)) for B in out)
    _verify_td(out,50,4)
    return tuple(out)


@lru_cache(maxsize=1)
def _trans_bsp22() -> Tuple[Block, ...]:
    """Return a deterministic TD(4,22) via Bose--Shrikhande--Parker.

    BSP, *Further results on the construction of mutually orthogonal Latin
    squares and the falsity of Euler's conjecture* (Canad. J. Math. 12
    (1960), Theorem 3 and Example 2), obtain two MOLS(22) by deleting
    three non-collinear treatments from a BIBD(25,5,1).  We implement that
    construction directly using the affine plane AG(2,5).

    After deleting three non-collinear points, the three shortened lines
    through pairs of deleted points are disjoint 3-blocks and form the
    "clear" component in BSP Theorem 1.  On those blocks we place full
    OA(4,3,3,2)s.  On every remaining 4- or 5-block we place BSP's
    distinct-pair matrix P: for order 4 the columns are the even
    permutations (A_4), and for order 5 they are the sharply 2-transitive
    affine permutations x -> ax+b of F_5, evaluated at four fixed inputs.
    Constant columns are added for points outside the three clear blocks.

    The resulting OA(22^2,4,22,2) is equivalent to TD(4,22).  No search is
    used.
    """
    q = 5

    # Affine plane AG(2,5): 25 points and 30 lines of size 5.
    pts = [(x,y) for x in range(q) for y in range(q)]
    lines: List[Tuple[Tuple[int,int], ...]] = []
    for c in range(q):
        lines.append(tuple((c,y) for y in range(q)))
    for m in range(q):
        for b in range(q):
            lines.append(tuple((x,(m*x+b)%q) for x in range(q)))

    deleted = {(0,0),(1,0),(0,1)}  # non-collinear
    remain = [p for p in pts if p not in deleted]
    pos = {p:i for i,p in enumerate(remain)}
    pbd: List[Tuple[int,...]] = []
    for L in lines:
        B = tuple(sorted(pos[p] for p in L if p not in deleted))
        if len(B) >= 2:
            pbd.append(B)

    # Strong PBD check and identify the three disjoint clear 3-blocks.
    pair_mult = Counter()
    for B in pbd:
        pair_mult.update(itertools.combinations(B,2))
    if len(pair_mult) != math.comb(22,2) or any(c != 1 for c in pair_mult.values()):
        raise AssertionError("BSP order-22 truncated AG(2,5) PBD failed")
    clear = [B for B in pbd if len(B) == 3]
    if len(clear) != 3 or len(set().union(*(set(B) for B in clear))) != 9:
        raise AssertionError("BSP order-22 clear 3-block component failed")
    if any(len(B) not in (3,4,5) for B in pbd):
        raise AssertionError("BSP order-22 PBD has an unexpected block size")

    columns: List[Tuple[int,int,int,int]] = []

    # Full OA(4,3,3,2) on each clear block.
    oa3 = trans_with_groups(3,4)
    local3 = [tuple((x-1)%3 for x in B) for B in oa3]
    for B in clear:
        D = tuple(sorted(B))
        for C in local3:
            columns.append(tuple(D[z] for z in C))

    # BSP distinct-pair matrices.  Each column contains pairwise distinct
    # symbols and every ordered distinct pair occurs once in every row pair.
    import itertools as _it
    p4 = [P for P in _it.permutations(range(4))
          if sum(P[i] > P[j] for i in range(4) for j in range(i+1,4)) % 2 == 0]
    if len(p4) != 12:
        raise AssertionError("A4 distinct-pair matrix has wrong size")
    p5 = [tuple((a*x+b)%5 for x in (0,1,2,3)) for a in range(1,5) for b in range(5)]
    if len(p5) != 20:
        raise AssertionError("AGL(1,5) distinct-pair matrix has wrong size")

    clear_set = set(clear)
    for B in pbd:
        if B in clear_set:
            continue
        D = tuple(sorted(B))
        local = p4 if len(D) == 4 else p5
        for C in local:
            columns.append(tuple(D[z] for z in C))

    # Treatments outside the clear component get their equal-pair columns.
    clear_points = set().union(*(set(B) for B in clear))
    for x in range(22):
        if x not in clear_points:
            columns.append((x,x,x,x))

    if len(columns) != 22*22:
        raise AssertionError(f"BSP OA(4,22) has {len(columns)} columns, expected 484")

    # Verify the OA property before converting to a transversal design.
    for r1 in range(4):
        for r2 in range(r1+1,4):
            seen = Counter((C[r1],C[r2]) for C in columns)
            if len(seen) != 22*22 or any(c != 1 for c in seen.values()):
                raise AssertionError("BSP OA(4,22) pair property failed")

    out = [tuple(row*22 + C[row] + 1 for row in range(4)) for C in columns]
    out = sorted(tuple(sorted(B)) for B in out)
    _verify_td(out,22,4)
    return tuple(out)

@lru_cache(maxsize=1)
def _trans_mills14() -> Tuple[Block, ...]:
    """Return Mills' explicit TD(4,14) ingredient.

    Mills, *On the Covering of Pairs by Quadruples I* (1972), p.74,
    constructs 187 transversal blocks on four groups whose second
    coordinate set is Z_11 union {u1,u2,u3}; these cover every cross-group
    pair except pairs for which both second coordinates lie in U={u1,u2,u3}.
    Filling that 3-point hole with the standard TD(4,3) gives a TD(4,14).

    This is the non-MacNeish ingredient required by Mills II, Lemma 3 at
    order 58, and hence by the finite order-259 seed.  It is completely
    deterministic and uses no search.
    """
    q = 14

    def P(group: int, value: int) -> int:
        return (group % 4) * q + value + 1

    def Z(group: int, t: int) -> int:
        return P(group, t % 11)

    # Values 0..10 represent Z_11; values 11,12,13 represent u1,u2,u3.
    out: List[Block] = []
    for t in range(11):
        out.append(tuple(Z(g, t) for g in range(4)))

    for r in range(4):
        for t in range(11):
            out.append((P(r,11), Z(r+1,t),   Z(r+2,t+4), Z(r+3,t+1)))
            out.append((P(r,12), Z(r+1,t),   Z(r+2,t+6), Z(r+3,t+2)))
            out.append((P(r,13), Z(r+1,t),   Z(r+2,t+9), Z(r+3,t+8)))
            out.append((Z(r,t),  Z(r+1,t+1), Z(r+2,t+4), Z(r+3,t+6)))

    # Fill the missing U x U cross-pairs by any TD(4,3).
    small = trans_trim(trans1(3, 1), 4)
    for B in small:
        mapped = []
        for x in B:
            group = (x - 1) // 3
            within = (x - 1) % 3
            mapped.append(P(group, 11 + within))
        out.append(tuple(mapped))

    assert len(out) == q * q
    return tuple(sorted(tuple(sorted(B)) for B in out))


@lru_cache(maxsize=1)
def _trans_pbd21() -> Tuple[Block, ...]:
    """Construct TD(5,21) by PBD closure over the projective plane of order 4.

    The 21 lines of PG(2,4) form a 2-(21,5,1) design.  On each 5-point
    line we place the incomplete orthogonal array obtained from TD(6,5) by
    deleting one parallel class and one coordinate.  After normalising the
    deleted class to the five constant columns, the remaining 20 columns
    cover every *unequal* ordered symbol pair exactly once in every pair of
    rows.  Combining these local arrays over the PBD and restoring the 21
    global constant columns gives OA(21^2,5,21,2), equivalently TD(5,21).

    This is a deterministic PBD/MOLS construction; it is included because
    order 21 is the first non-MacNeish three-MOLS parameter reached by
    Mills' Lemma 2 recursion.
    """
    # Projective plane PG(2,4) as AG(2,4) plus its line at infinity.
    p, degree, q = 2, 2, 4
    def A(x: int, y: int) -> int:
        return q*x + y  # affine points 0..15
    def I(slope: int) -> int:
        return 16 + slope  # slopes 0..3 and vertical=4

    pbd: List[Tuple[int, ...]] = []
    for a in range(q):
        for b in range(q):
            line = [A(x, _gf_add(_gf_mul(a, x, p, degree), b, p, degree)) for x in range(q)]
            line.append(I(a))
            pbd.append(tuple(sorted(line)))
    for c in range(q):
        pbd.append(tuple(sorted([A(c,y) for y in range(q)] + [I(q)])))
    pbd.append(tuple(range(16,21)))

    # Sanity-check the 2-(21,5,1) property locally, without importing any
    # covering/search machinery.
    from collections import Counter
    pair_mult = Counter()
    for B in pbd:
        pair_mult.update(itertools.combinations(B,2))
    if len(pbd) != 21 or len(pair_mult) != 210 or any(c != 1 for c in pair_mult.values()):
        raise AssertionError("internal PG(2,4) construction failed")

    # Start from TD(6,5).  Sacrifice the last coordinate and the fibre in
    # which that coordinate is 0.  Normalise that fibre to the five constant
    # columns in the remaining five coordinates.
    td65 = trans_trim(trans1(5,1), 6)
    raw_cols = [tuple((x-1) % 5 for x in B) for B in td65]
    deleted = [C for C in raw_cols if C[5] == 0]
    if len(deleted) != 5:
        raise AssertionError("TD(6,5) fibre has wrong size")
    deleted.sort(key=lambda C: C[0])
    relabel: List[Dict[int,int]] = []
    for row in range(5):
        perm = {C[row]: C[0] for C in deleted}
        if set(perm) != set(range(5)) or set(perm.values()) != set(range(5)):
            raise AssertionError("failed to normalise TD(6,5) parallel class")
        relabel.append(perm)

    local: List[Tuple[int,...]] = []
    for C in raw_cols:
        norm = tuple(relabel[row][C[row]] for row in range(5))
        if C[5] == 0:
            if len(set(norm)) != 1:
                raise AssertionError("deleted OA column is not constant after normalisation")
            continue
        local.append(norm)
    if len(local) != 20:
        raise AssertionError("incomplete OA(5,5) has wrong number of columns")

    # Verify the local incomplete-array property: in every pair of rows, all
    # ordered pairs (a,b), a != b, occur once and no diagonal pair occurs.
    for r1 in range(5):
        for r2 in range(r1+1,5):
            seen = Counter((C[r1],C[r2]) for C in local)
            want = {(a,b) for a in range(5) for b in range(5) if a != b}
            if set(seen) != want or any(c != 1 for c in seen.values()):
                raise AssertionError("local incomplete OA property failed")

    # PBD closure.  Equal ordered pairs are supplied by global constant
    # columns; unequal pairs are supplied in their unique projective-plane
    # line.
    columns: List[Tuple[int,...]] = [(x,x,x,x,x) for x in range(21)]
    for B in pbd:
        ordered = tuple(sorted(B))
        for C in local:
            columns.append(tuple(ordered[z] for z in C))
    if len(columns) != 21*21:
        raise AssertionError("OA(5,21) has wrong number of columns")

    # Convert the orthogonal array to a transversal design on five groups.
    out = [tuple(row*21 + C[row] + 1 for row in range(5)) for C in columns]

    # Strong pair check for the finite ingredient.
    cross = Counter()
    for B in out:
        for x,y in itertools.combinations(B,2):
            if (x-1)//21 == (y-1)//21:
                raise AssertionError("TD(5,21) block meets a group twice")
            cross[tuple(sorted((x,y)))] += 1
    if len(cross) != math.comb(5,2)*21*21 or any(c != 1 for c in cross.values()):
        raise AssertionError("internal TD(5,21) verification failed")
    return tuple(sorted(tuple(sorted(B)) for B in out))


@lru_cache(maxsize=1)
def _trans_roth_peters24() -> Tuple[Block, ...]:
    """Return a deterministic TD(6,24) from the Roth--Peters MOLS.

    Roth and Peters constructed four pairwise orthogonal Latin squares of
    order 24 on the group Z_6 x Z_2 x Z_2.  We encode the four generating
    rows in the later Wallis--Zhu normalisation reproduced in the literature.
    If S=(s_i) and P=(p_j), the Latin square L_S(P) has entry s_i p_j.
    Row, column, and the four square entries therefore form a TD(6,24).

    This fixed published ingredient is used only to bridge the exceptional
    three-MOLS parameter 24 in Mills' Lemma 2; there is no run-time search.
    """
    Element = Tuple[int,int,int]
    def E(a: int = 0, b: int = 0, c: int = 0) -> Element:
        return (a % 6, b % 2, c % 2)
    def mul(x: Element, y: Element) -> Element:
        return ((x[0]+y[0])%6, (x[1]+y[1])%2, (x[2]+y[2])%2)

    S = [
        E(0),E(5),E(4),E(3),E(2),E(1),
        E(0,1),E(5,1),E(4,1),E(3,1),E(2,1),E(1,1),
        E(1,0,1),E(2,0,1),E(3,0,1),E(4,0,1),E(5,0,1),E(0,0,1),
        E(1,1,1),E(2,1,1),E(3,1,1),E(4,1,1),E(5,1,1),E(0,1,1),
    ]
    P1 = [
        E(0),E(1),E(2),E(3),E(4),E(5),
        E(0,1),E(1,1),E(2,1),E(3,1),E(4,1),E(5,1),
        E(5,0,1),E(4,0,1),E(3,0,1),E(2,0,1),E(1,0,1),E(0,0,1),
        E(5,1,1),E(4,1,1),E(3,1,1),E(2,1,1),E(1,1,1),E(0,1,1),
    ]
    P2 = [
        E(0),E(3),E(5,1),E(2,0,1),E(2,1),E(3,0,1),
        E(0,0,1),E(4,1,1),E(1,0,1),E(4),E(5,1,1),E(1),
        E(1,1),E(5,0,1),E(4,1),E(1,1,1),E(4,0,1),E(0,1,1),
        E(3,1,1),E(2),E(2,1,1),E(5),E(3,1),E(0,1),
    ]
    P3 = [
        E(0),E(2),E(4),E(5,0,1),E(3,1,1),E(4,1),
        E(0,1,1),E(2,1,1),E(5,1,1),E(1,1),E(1),E(3,0,1),
        E(3),E(1,0,1),E(1,1,1),E(5,1),E(2,1),E(0,1),
        E(4,1,1),E(3,1),E(5),E(4,0,1),E(2,0,1),E(0,0,1),
    ]
    P4 = [
        E(0),E(2,1),E(2,1,1),E(4,1,1),E(5,0,1),E(1,1),
        E(4,0,1),E(0,1),E(5),E(0,1,1),E(3,0,1),E(4),
        E(1),E(0,0,1),E(3,1,1),E(2),E(3,1),E(1,0,1),
        E(4,1),E(2,0,1),E(1,1,1),E(5,1,1),E(5,1),E(3),
    ]
    rows = (P1,P2,P3,P4)
    if any(len(P) != 24 or len(set(P)) != 24 for P in (S,*rows)):
        raise AssertionError("Roth--Peters generating row is not a permutation")

    # A fixed canonical numbering of the group elements.
    elements = [E(a,b,c) for c in range(2) for b in range(2) for a in range(6)]
    index = {x:i for i,x in enumerate(elements)}
    out: List[Block] = []
    for i in range(24):
        for j in range(24):
            coords = [i, j]
            coords.extend(index[mul(S[i],P[j])] for P in rows)
            out.append(tuple(g*24 + x + 1 for g,x in enumerate(coords)))

    # Verify the full TD property once when this cached ingredient is built.
    from collections import Counter
    mult = Counter()
    for B in out:
        for x,y in itertools.combinations(B,2):
            if (x-1)//24 == (y-1)//24:
                raise AssertionError("Roth--Peters TD block repeats a group")
            mult[tuple(sorted((x,y)))] += 1
    if len(mult) != math.comb(6,2)*24*24 or any(c != 1 for c in mult.values()):
        raise AssertionError("Roth--Peters TD(6,24) verification failed")
    return tuple(sorted(tuple(sorted(B)) for B in out))

def _macneish_group_capacity(r: int) -> int:
    """Cheap group-count bound supplied by the MacNeish product."""
    factors = prime_factor_mult(int(r))
    return min(p ** e for p, e in factors.items()) + 1


def transversal_group_capacity(r: int) -> int:
    """Return the largest TD(s,r) group count currently constructible.

    The baseline is the MacNeish product.  Source-based finite ingredients
    improve the capacity at the exceptional orders needed by Mills' recursion.
    The calculation is deliberately cheap and does not materialise r^2 blocks.
    """
    cap = _macneish_group_capacity(r)
    explicit = {
        10: 4,
        12: 7,
        14: 4,
        21: 5,
        22: 4,
        24: 6,
        26: 4,
        38: 4,
        50: 4,
    }
    return max(cap, explicit.get(int(r), 0))


def trans_with_groups(r: int, s: int) -> List[Block]:
    """Construct a TD(s,r) from deterministic available ingredients.

    Route selection is performed before materialising any design.  Earlier
    versions always built the MacNeish TD first and sometimes threw it away
    when an explicit non-MacNeish ingredient was required.
    """
    r = int(r)
    s = int(s)
    if s < 2:
        raise ValueError("a transversal design needs at least two groups")

    # Use MacNeish whenever it already has enough groups; this keeps the usual
    # algebraic route and avoids loading a larger finite seed unnecessarily.
    mac_cap = _macneish_group_capacity(r)
    if mac_cap >= s:
        return trans_trim(trans2(r), s)

    explicit = {
        10: (4, _trans_mills10),
        12: (7, _trans_bck12),
        14: (4, _trans_mills14),
        21: (5, _trans_pbd21),
        22: (4, _trans_bsp22),
        24: (6, _trans_roth_peters24),
        26: (4, _trans_bsp26),
        38: (4, _trans_mills38),
        50: (4, _trans_mills50),
    }
    entry = explicit.get(r)
    if entry is not None and s <= entry[0]:
        return trans_trim(entry[1](), s)

    raise NotImplementedError(
        f"no deterministic TD({s},{r}) ingredient is registered; "
        f"MacNeish supplies only {mac_cap} groups"
    )

def truncate(blocks: Iterable[Sequence[int]], r1: int) -> List[Block]:
    """Truncate the last group of TD(s,r) from r points to r1 points."""
    b = list(blocks)
    if not b:
        return []
    r = math.isqrt(len(b))
    if r * r != len(b):
        raise ValueError("transversal design must have r^2 blocks")
    if not 0 <= r1 <= r:
        raise ValueError(f"r1={r1} must satisfy 0 <= r1 <= r={r}")
    t = r - r1
    if t == 0:
        return [tuple(x for x in block) for block in b]
    cutoff = r * len(b[0]) - t
    return [tuple(e for e in block if e <= cutoff) for block in b]
