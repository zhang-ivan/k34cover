from collections import Counter, defaultdict
from typing import Iterable, List, Tuple, Dict, Any
import math



import bibd

def _normalize_blocks(blocks: Iterable[Iterable[int]]) -> List[Tuple[int, ...]]:
    norm = sorted(set(tuple(sorted(B)) for B in blocks))
    return norm


def _auto_reindex_if_needed(v: int, blocks: List[Tuple[int, ...]]) -> List[Tuple[int, ...]]:
    pts = [x for B in blocks for x in B]
    if not pts:
        return blocks
    mn, mx = min(pts), max(pts)
    if mn == 1 and mx == v:
        return [tuple(x-1 for x in B) for B in blocks]
    return blocks


def verify_bibd(v: int,
                blocks: Iterable[Iterable[int]],
                k: int = 4,
                lambd: int = 1,
                auto_reindex: bool = True,
                early_exit: bool = False) -> Tuple[bool, Dict[str, Any]]:
    rep: Dict[str, Any] = {}
    B = _normalize_blocks(blocks)
    if auto_reindex:
        B = _auto_reindex_if_needed(v, B)
    rep["v"] = v
    rep["k_expected"] = k
    rep["lambda_expected"] = lambd
    rep["b"] = len(B)
    rep["blocks_sample"] = B[:5]

    if rep["b"] == 0:
        rep["error"] = "Empty block list."
        return False, rep

    k_set = set(len(b) for b in B)
    if k_set != {k}:
        rep["error"] = f"Inconsistent block sizes: seen {sorted(k_set)} but expected {k}."
        if early_exit:
            return False, rep

    for b in B:
        for x in b:
            if x < 0 or x >= v:
                rep["error_range"] = rep.get("error_range", []) + [f"Out-of-range point {x} in block {b} (expect 0..{v-1})."]
                if early_exit:
                    return False, rep

    r_count = Counter()
    for b in B:
        for x in b:
            r_count[x] += 1
    if len(r_count) != v:
        rep["error_missing_points"] = [p for p in range(v) if p not in r_count]
        if early_exit:
            return False, rep

    r_values = list(r_count.values())
    r_uniques = sorted(set(r_values))
    rep["r_values_unique"] = r_uniques
    if len(r_uniques) != 1:
        rep["error_r_nonuniform"] = True
        rep["r_histogram"] = dict(Counter(r_values).most_common())
        if early_exit:
            return False, rep
    r_emp = r_uniques[0] if r_uniques else None
    rep["r_empirical"] = r_emp

    rep["check_vr_eq_bk"] = (v * r_emp == rep["b"] * k) if r_emp is not None else False
    rep["check_param_identity"] = (r_emp * (k - 1) == lambd * (v - 1)) if r_emp is not None else False

    pair = Counter()
    for b in B:
        sb = sorted(b)
        for i in range(k):
            for j in range(i+1, k):
                pair[(sb[i], sb[j])] += 1

    expected_pairs = v * (v - 1) // 2
    rep["pairs_seen"] = len(pair)
    rep["pairs_expected"] = expected_pairs
    if rep["pairs_seen"] != expected_pairs:
        rep["error_pair_coverage"] = f"Seen {rep['pairs_seen']} pairs but expected {expected_pairs}."
        if early_exit:
            return False, rep

    lambdas = list(pair.values())
    lam_uniques = sorted(set(lambdas))
    rep["lambda_values_unique"] = lam_uniques
    if lam_uniques != [lambd]:
        rep["error_lambda_nonuniform"] = True
        high = Counter(pair).most_common(5)
        low = sorted(pair.items(), key=lambda kv: kv[1])[:5]
        rep["lambda_examples_high"] = [(p, c) for p, c in high]
        rep["lambda_examples_low"]  = [(p, c) for p, c in low]
        if early_exit:
            return False, rep

    ok = True
    if k_set != {k} or \
       len(r_uniques) != 1 or \
       not rep["check_vr_eq_bk"] or \
       not rep["check_param_identity"] or \
       rep.get("pairs_seen") != expected_pairs or \
       lam_uniques != [lambd]:
        ok = False

    rep["ok"] = ok
    return ok, rep


def summary(rep: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"BIBD check: v={rep.get('v')}, k={rep.get('k_expected')}, λ={rep.get('lambda_expected')}, b={rep.get('b')}")
    if "r_empirical" in rep:
        lines.append(f"Replication r={rep['r_empirical']}")
    if "r_values_unique" in rep:
        lines.append(f"r-values present: {rep['r_values_unique']}")
    if "lambda_values_unique" in rep:
        lines.append(f"λ-values present on pairs: {rep['lambda_values_unique']}")
    lines.append(f"vr=bk? {rep.get('check_vr_eq_bk')}")
    lines.append(f"r(k-1)=λ(v-1)? {rep.get('check_param_identity')}")
    if rep.get("error"):
        lines.append(f"ERROR: {rep['error']}")
    if rep.get("error_range"):
        lines.append(f"Range errors (first 3): {rep['error_range'][:3]}")
    if rep.get("error_missing_points"):
        lines.append(f"Missing points: {rep['error_missing_points'][:10]}")
    if rep.get("error_r_nonuniform"):
        lines.append(f"Non-uniform r; histogram (top): {list(rep.get('r_histogram', {}).items())[:5]}")
    if rep.get("error_pair_coverage"):
        lines.append(rep["error_pair_coverage"])
    if rep.get("error_lambda_nonuniform"):
        lines.append("Non-uniform λ; examples:")
        lines.append(f"  High (pair->count): {rep.get('lambda_examples_high')}")
        lines.append(f"  Low  (pair->count): {rep.get('lambda_examples_low')}")
    lines.append(f"OK? {rep.get('ok')}")
    return "\n".join(lines)

if __name__ == '__main__':
    v=1201
    blocks = bibd.bibd4(v)
    ok, report = verify_bibd(v, blocks, k=4, lambd=1, auto_reindex=True)
    print(summary(report))