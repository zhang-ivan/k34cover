"""Verification and arithmetic checks for K3/K4 coverings."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterable, List, Sequence, Tuple

Block = Tuple[int, ...]
Edge = Tuple[int, int]


@dataclass(frozen=True)
class CoverAnalysis:
    v: int
    n_k3: int
    n_k4: int
    excess_size: int
    excess: List[Edge]
    missing_edges: List[Edge]
    multiplicities: Dict[Edge, int]


def optimal_parameters(v: int) -> Tuple[int, int, int]:
    """Return ``(xi, alpha, beta)`` for the optimum minimum-excess cover.

    Here ``alpha`` and ``beta`` are the numbers of K3 and K4 blocks.  The
    formulas are the established optimum values used by the project, with the
    exceptional small orders 6, 8, 9, 10, 17, 18 and 19 inserted explicitly.
    """
    if v < 3:
        raise ValueError("v must be at least 3")
    special = {
        6: (3, 0, 3),
        8: (2, 4, 3),
        9: (0, 12, 0),
        10: (0, 9, 3),
        17: (2, 12, 17),
        18: (0, 15, 18),
        19: (0, 13, 22),
    }
    if v in special:
        return special[v]

    r = v % 12
    if r in (1, 4):
        return 0, 0, (v * v - v) // 12
    if r in (7, 10):
        return 0, 7, (v * v - v - 42) // 12
    if r in (0, 3):
        return 0, v // 3, (v * v - 3 * v) // 12
    if r in (6, 9):
        return 0, (v + 3) // 3, (v * v - 3 * v - 6) // 12
    if r in (5, 8):
        return 2, (2 * v - 4) // 3, (v * v - 5 * v + 12) // 12
    if r in (2, 11):
        return 2, (2 * v - 1) // 3, (v * v - 5 * v + 6) // 12
    raise AssertionError("unreachable residue class")


def analyse_cover(v: int, blocks: Iterable[Sequence[int]]) -> CoverAnalysis:
    """Analyse edge multiplicities of a K3/K4 block list."""
    multiplicity: Counter[Edge] = Counter()
    n_k3 = 0
    n_k4 = 0

    for raw in blocks:
        block = tuple(sorted(map(int, raw)))
        if len(block) not in (3, 4):
            raise ValueError(f"wrong block size {len(block)} for block {raw}")
        if len(set(block)) != len(block):
            raise ValueError(f"repeated vertex inside block {raw}")
        if block[0] < 1 or block[-1] > v:
            raise ValueError(f"block {raw} contains a vertex outside 1..{v}")
        if len(block) == 3:
            n_k3 += 1
        else:
            n_k4 += 1
        multiplicity.update((a, b) for a, b in combinations(block, 2))

    expected_edges = v * (v - 1) // 2

    # On the successful path every multiplicity key is already known to be a
    # legitimate edge of K_v.  Hence seeing exactly C(v,2) distinct keys proves
    # that no edge is missing; avoid materialising the full O(v^2) edge list.
    if len(multiplicity) == expected_edges:
        missing: List[Edge] = []
    else:
        missing = [
            (a, b)
            for a in range(1, v + 1)
            for b in range(a + 1, v + 1)
            if (a, b) not in multiplicity
        ]

    excess: List[Edge] = []
    for e, count in multiplicity.items():
        if count > 1:
            excess.extend([e] * (count - 1))
    excess.sort()

    return CoverAnalysis(
        v=v,
        n_k3=n_k3,
        n_k4=n_k4,
        excess_size=len(excess),
        excess=excess,
        missing_edges=missing,
        multiplicities=dict(multiplicity),
    )


def k3k4cover_checker(v: int, input_design_: Iterable[Sequence[int]]) -> bool:
    """Assert that ``input_design_`` is an optimum minimum-excess K3/K4 cover."""
    analysis = analyse_cover(v, input_design_)
    xi, alpha, beta = optimal_parameters(v)

    errors = []
    if analysis.missing_edges:
        errors.append(f"{len(analysis.missing_edges)} uncovered edge(s), first={analysis.missing_edges[:5]}")
    if analysis.excess_size != xi:
        errors.append(f"excess {analysis.excess_size}, expected {xi}")
    if analysis.n_k3 != alpha:
        errors.append(f"K3 count {analysis.n_k3}, expected {alpha}")
    if analysis.n_k4 != beta:
        errors.append(f"K4 count {analysis.n_k4}, expected {beta}")

    assert not errors, f"Check failed for order={v}: " + "; ".join(errors)
    return True


def sort_list_of_tuples(original_cover: Iterable[Sequence[int]]) -> List[Block]:
    return sorted((tuple(sorted(t)) for t in original_cover), key=lambda x: (len(x), x))


# Backward-compatible spelling retained for old callers.
def sort_lost_of_tuples(original_cover: Iterable[Sequence[int]]) -> List[Block]:
    return sort_list_of_tuples(original_cover)


def count_k3_k4(cover: Iterable[Sequence[int]]) -> Tuple[int, int]:
    blocks = list(cover)
    alpha = sum(1 for b in blocks if len(b) == 3)
    beta = sum(1 for b in blocks if len(b) == 4)
    if alpha + beta != len(blocks):
        raise ValueError("cover contains a block whose size is not 3 or 4")
    return alpha, beta
