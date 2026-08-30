"""Construct optimum minimum-excess coverings of K_v by K3 and K4.

The public construction is organised around three theorem-level templates:

* direct truncation of a 2-(n,4,1) design for residues 0,1,2,3,4,11 mod 12;
* truncation/filling of a PBD(n,{4,7*},1) for residues 5,7,8,10 mod 12;
* the Mills/Colbourn--Rosa--Stinson truncation for residues 6,9 mod 12.

A small set of fixed finite optimum seeds is stored alongside these families.
No exact-cover, SAT, ILP, or other combinatorial search is invoked at run time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from k34cover.designs import small
from k34cover.verify import analyse_cover, optimal_parameters

Block = Tuple[int, ...]
Edge = Tuple[int, int]


@dataclass(frozen=True)
class CoverResult:
    v: int
    blocks: List[Block]
    # Repeated edge occurrences.  An edge appears m-1 times here if it is
    # covered m times.  Thus K8 has the same edge twice in xi.
    xi: List[Edge]
    n_k3: int
    n_k4: int


def _normalise(blocks: Iterable[Sequence[int]]) -> List[Block]:
    return sorted((tuple(sorted(map(int, b))) for b in blocks), key=lambda b: (len(b), b))


def _result(v: int, blocks: Iterable[Sequence[int]]) -> CoverResult:
    """Normalise, verify once, and package a constructed cover.

    The old front end checked only that no pair was missed and the CLI then
    performed a second full verification pass.  The constructor now checks all
    theorem parameters here, so callers can trust a returned :class:`CoverResult`
    without immediately rescanning O(v^2) pairs.
    """
    cover = _normalise(blocks)
    analysis = analyse_cover(v, cover)
    xi, alpha, beta = optimal_parameters(v)

    errors = []
    if analysis.missing_edges:
        errors.append(
            f"{len(analysis.missing_edges)} uncovered edge(s), "
            f"first={analysis.missing_edges[:5]}"
        )
    if analysis.excess_size != xi:
        errors.append(f"excess {analysis.excess_size}, expected {xi}")
    if analysis.n_k3 != alpha:
        errors.append(f"K3 count {analysis.n_k3}, expected {alpha}")
    if analysis.n_k4 != beta:
        errors.append(f"K4 count {analysis.n_k4}, expected {beta}")
    if errors:
        raise AssertionError(f"internal construction error for v={v}: " + "; ".join(errors))

    return CoverResult(
        v=v,
        blocks=cover,
        xi=analysis.excess,
        n_k3=analysis.n_k3,
        n_k4=analysis.n_k4,
    )


def _truncate_and_relabel(
    source_n: int,
    blocks: Iterable[Sequence[int]],
    deleted: Iterable[int],
    *,
    allowed_sizes: Tuple[int, ...],
) -> Tuple[List[Block], dict[int, int]]:
    """Delete points, relabel survivors to 1..n, and retain allowed blocks.

    This factors the mechanical part shared by the hole-7 and Mills
    truncations.  Blocks reduced to a size outside ``allowed_sizes`` are not
    silently discarded: they trigger an assertion so theorem-specific code
    remains responsible for any exceptional remnant (such as the 2-set in the
    two-point BIBD truncation).
    """
    deleted_set = {int(x) for x in deleted}
    if not deleted_set.issubset(range(1, source_n + 1)):
        raise ValueError("deleted point lies outside the source point set")
    surviving = [x for x in range(1, source_n + 1) if x not in deleted_set]
    relabel = {old: new for new, old in enumerate(surviving, start=1)}

    out: List[Block] = []
    for raw in blocks:
        source_block = tuple(map(int, raw))
        reduced = tuple(x for x in source_block if x not in deleted_set)
        if len(reduced) not in allowed_sizes:
            raise AssertionError(
                f"truncation of block {source_block} produced size {len(reduced)}, "
                f"expected one of {allowed_sizes}"
            )
        out.append(tuple(sorted(relabel[x] for x in reduced)))
    return out, relabel


def _cover_from_bibd4_truncation(v: int) -> List[Block]:
    """One BIBD(4) template for residues 0,1,2,3,4,11 modulo 12.

    Let ``s`` be 0, 1, or 2 so that ``v+s == 1 or 4 (mod 12)``.  Build a
    BIBD(v+s,4,1) and delete its last ``s`` points.

    * s=0: the BIBD itself is the optimum cover;
    * s=1: incident K4s simply become the required K3 groups;
    * s=2: the unique K4 through both deleted points leaves one uncovered
      surviving pair.  Discard that 2-set and add one triangle through that
      pair, producing exactly the required two-edge excess.

    This replaces both the old group-relabel/fill branch and the recursive
    v+1 -> v branch for residues 2,11.
    """
    from k34cover.designs import bibd4

    r = v % 12
    if r in (1, 4):
        s = 0
    elif r in (0, 3):
        s = 1
    elif r in (2, 11):
        s = 2
    else:
        raise ValueError("BIBD truncation is not the route for this residue class")

    source_n = v + s
    design = bibd4.bibd4(source_n)
    if s == 0:
        return list(design)

    deleted = set(range(v + 1, source_n + 1))
    blocks: List[Block] = []
    pair_remnants: List[Tuple[int, int]] = []
    for raw in design:
        reduced = tuple(sorted(x for x in raw if x not in deleted))
        if len(reduced) in (3, 4):
            blocks.append(reduced)
        elif s == 2 and len(reduced) == 2:
            pair_remnants.append(reduced)
        else:
            raise AssertionError("unexpected BIBD block size after truncation")

    if s == 1:
        if pair_remnants:
            raise AssertionError("one-point BIBD truncation produced a 2-set")
        return blocks

    if len(pair_remnants) != 1:
        raise AssertionError(
            f"two-point BIBD truncation produced {len(pair_remnants)} pair remnants"
        )
    a, b = pair_remnants[0]
    # Any surviving third point works: all pairs except ab are already covered
    # once, so adding (a,b,z) covers ab and repeats exactly az and bz.
    z = next(x for x in range(1, v + 1) if x not in (a, b))
    blocks.append(tuple(sorted((a, b, z))))
    return blocks


def _cover_from_hole7_truncation(v: int) -> List[Block]:
    """One 7-hole PBD template for residues 5,7,8,10 modulo 12.

    Residues 7,10 fill the 7-hole by the Fano plane.  Residues 5,8 start at
    order v+2, delete two points of the distinguished hole, and fill the
    surviving 5-set by the fixed optimum K5 seed.  The same routine covers the
    formerly special orders 5,7,20,22.
    """
    from k34cover.designs import hole7

    r = v % 12
    if r in (7, 10):
        external, hole = hole7.pbd_hole7(v)
        return list(external) + small.fano7(hole)
    if r not in (5, 8):
        raise ValueError("7-hole truncation is not the route for this residue class")

    source_n = v + 2
    external, hole = hole7.pbd_hole7(source_n)
    deleted = tuple(hole[-2:])
    deleted_set = set(deleted)
    blocks, relabel = _truncate_and_relabel(
        source_n,
        external,
        deleted,
        allowed_sizes=(3, 4),
    )
    remaining_hole = tuple(relabel[x] for x in hole if x not in deleted_set)
    if len(remaining_hole) != 5:
        raise AssertionError("7-hole truncation did not leave a 5-set")
    blocks.extend(small.relabel(small.cover5(), tuple(range(1, 6)), remaining_hole))
    return blocks


def _cover_from_mills_truncation(v: int) -> List[Block]:
    """Colbourn--Rosa--Stinson Lemma 3.15 from Mills' optimum K4 cover.

    Mills' optimum K4 cover of order v+1 has a unique pair covered four
    times.  Delete either endpoint of that pair; every incident K4 becomes a
    K3 and the repeated-pair excess disappears, leaving an exact PBD on v
    points with (v+3)/3 triples.
    """
    from k34cover.designs import mills

    source_n = v + 1
    source = mills.mills_k4_cover(source_n)
    missing, repeated = mills.analyse_k4_cover(source_n, source)
    if missing or len(repeated) != 3 or len(set(repeated)) != 1:
        raise AssertionError(f"unexpected Mills excess at order {source_n}")
    delete = repeated[0][0]
    blocks, _ = _truncate_and_relabel(
        source_n,
        source,
        (delete,),
        allowed_sizes=(3, 4),
    )
    return blocks


# Fixed finite optimum seeds used by the top-level dispatcher.
_FIXED_SEEDS = {
    6: small.cover6,
    8: small.cover8,
    9: small.sts9,
    10: small.cover10,
    17: small.cover17,
    18: small.cover18,
    19: small.cover19,
}



def prepare_generation(orders: Iterable[int]) -> None:
    """Pre-import the construction backends needed for ``orders``.

    This function performs import-only initialisation.  The CLI calls it once
    before starting per-order timers so Python module-loading cost is reported
    separately rather than being attributed to whichever order happens to be
    generated first.  No design is constructed and no construction cache is
    populated here.
    """
    need_bibd = False
    need_hole7 = False
    need_mills = False
    for raw in orders:
        v = int(raw)
        if v < 3:
            raise ValueError("v must be at least 3")
        if v in _FIXED_SEEDS:
            continue
        r = v % 12
        if r in (0, 1, 2, 3, 4, 11):
            need_bibd = True
        elif r in (5, 7, 8, 10):
            need_hole7 = True
        elif r in (6, 9):
            need_mills = True

    # Import the narrowest requested modules explicitly.  hole7 imports its
    # own dependencies, but keeping the calls explicit makes the timing
    # boundary stable if those module internals are reorganised later.
    import importlib

    if need_bibd:
        importlib.import_module("k34cover.designs.bibd4")
    if need_hole7:
        importlib.import_module("k34cover.designs.hole7")
    if need_mills:
        importlib.import_module("k34cover.designs.mills")

def cover_k3k4(v: int) -> CoverResult:
    """Construct an optimum minimum-excess {K3,K4}-cover of K_v.

    Every order ``v >= 3`` is implemented.  All returned results have already
    passed the full arithmetic/edge-multiplicity checker.
    """
    v = int(v)
    if v < 3:
        raise ValueError("v must be at least 3")
    if v in _FIXED_SEEDS:
        return _result(v, _FIXED_SEEDS[v]())

    r = v % 12
    if r in (0, 1, 2, 3, 4, 11):
        return _result(v, _cover_from_bibd4_truncation(v))
    if r in (5, 7, 8, 10):
        return _result(v, _cover_from_hole7_truncation(v))
    if r in (6, 9):
        return _result(v, _cover_from_mills_truncation(v))
    raise AssertionError(f"unreachable residue class for v={v}")
