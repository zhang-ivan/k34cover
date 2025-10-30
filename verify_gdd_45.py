# ================= HEADER =================
from collections import Counter, defaultdict
from itertools import combinations
from typing import Iterable, List, Tuple, Dict, Any, Set
# ==========================================



def _normalize_blocks(blocks: Iterable[Iterable[int]]) -> List[Tuple[int, ...]]:
    return sorted(set(tuple(sorted(B)) for B in blocks))


def _auto_reindex_blocks(u: int, blocks: List[Tuple[int, ...]]) -> List[Tuple[int, ...]]:
    pts = [x for b in blocks for x in b]
    if not pts:
        return blocks
    mn, mx = min(pts), max(pts)
    if mn == 0 and mx == u-1:
        return [tuple(x+1 for x in b) for b in blocks]
    return blocks


def _check_groups_partition(u: int, groups: Iterable[Iterable[int]]) -> Tuple[bool, str]:
    seen: Set[int] = set()
    for G in groups:
        for x in G:
            if x in seen:
                return False, f"Point {x} appears in more than one group."
            if x < 1 or x > u:
                return False, f"Point {x} in group out of range 1..{u}."
            seen.add(x)
    missing = [x for x in range(1, u+1) if x not in seen]
    if missing:
        return False, f"Missing points in groups: {missing[:10]} (and possibly more)."
    return True, ""


def verify_gdd_45(u: int,
                  design: Iterable[Iterable[int]],
                  groups: Iterable[Iterable[int]],
                  early_exit: bool = False) -> Tuple[bool, Dict[str, Any]]:
    rep: Dict[str, Any] = {"u": u}
    G = [tuple(sorted(g)) for g in groups]
    ok_part, msg = _check_groups_partition(u, G)
    rep["groups_ok"] = ok_part
    rep["groups_error"] = msg if not ok_part else None
    p2g: Dict[int, int] = {}
    for gi, grp in enumerate(G):
        for x in grp:
            p2g[x] = gi
    B = _normalize_blocks(design)
    B = _auto_reindex_blocks(u, B)
    rep["b"] = len(B)
    rep["block_sizes_present"] = sorted(set(len(b) for b in B))
    rep["size_ok"] = set(rep["block_sizes_present"]).issubset({4,5})
    if not rep["size_ok"] and early_exit:
        rep["ok"] = False
        return False, rep
    same_group_viol = []
    for b in B:
        gset = [p2g.get(x, None) for x in b]
        if None in gset:
            same_group_viol.append(("point-not-in-groups", b))
            if early_exit: break
        if len(set(gset)) != len(gset):
            same_group_viol.append(("two-in-same-group", b))
            if early_exit: break
    rep["same_group_violations"] = same_group_viol[:10]
    if same_group_viol and early_exit:
        rep["ok"] = False
        return False, rep

    from itertools import combinations
    pair = Counter()
    for b in B:
        for a,c in combinations(b,2):
            if p2g[a] == p2g[c]:
                rep.setdefault("intragroup_pair_in_block", []).append((a,c,b))
                if early_exit:
                    rep["ok"]=False
                    return False, rep
            else:
                pair[(min(a,c), max(a,c))]+=1

    group_sizes = [len(gr) for gr in G]
    total_pairs = 0
    for i in range(len(G)):
        for j in range(i+1, len(G)):
            total_pairs += group_sizes[i]*group_sizes[j]
    rep["pairs_expected"] = total_pairs
    rep["pairs_seen"] = len(pair)

    if rep["pairs_seen"] != total_pairs:
        missing = []
        for i in range(len(G)):
            for a in G[i]:
                for j in range(i+1, len(G)):
                    for c in G[j]:
                        if (min(a,c),max(a,c)) not in pair:
                            missing.append((a,c))
                            if len(missing)>=10: break
                    if len(missing)>=10: break
                if len(missing)>=10: break
            if len(missing)>=10: break
        rep["missing_cross_pairs_examples"] = missing

    lam_vals = sorted(set(pair.values()))
    rep["lambda_values_unique"] = lam_vals

    ok = (ok_part and rep["size_ok"] and
          rep["pairs_seen"] == total_pairs and
          lam_vals == [1] and
          not rep.get("intragroup_pair_in_block") and
          not rep.get("same_group_violations"))
    rep["ok"] = ok
    return ok, rep


def summary(rep: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"GDD(4,5) check: u={rep.get('u')}  b={rep.get('b')}")
    lines.append(f"block sizes present {rep.get('block_sizes_present')} size_ok={rep.get('size_ok')}")
    if not rep.get("groups_ok", True):
        lines.append(f"Groups error: {rep.get('groups_error')}")
    lines.append(f"cross-group pairs: {rep.get('pairs_seen')}/{rep.get('pairs_expected')}  λ-values {rep.get('lambda_values_unique')}")
    if rep.get("missing_cross_pairs_examples"):
        lines.append(f"missing examples: {rep['missing_cross_pairs_examples']}")
    if rep.get("same_group_violations"):
        lines.append(f"violations (sample): {rep['same_group_violations']}")
    lines.append(f"OK? {rep.get('ok')}")
    return "\n".join(lines)


