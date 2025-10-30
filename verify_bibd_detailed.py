from collections import Counter, defaultdict
from typing import Iterable, List, Tuple, Dict, Any
import math

import bibd

def _normalize_blocks(blocks: Iterable[Iterable[int]]) -> List[Tuple[int, ...]]:
    return sorted(set(tuple(sorted(B)) for B in blocks))


def _auto_reindex_if_needed(v: int, blocks: List[Tuple[int, ...]]) -> List[Tuple[int, ...]]:
    pts = [x for B in blocks for x in B]
    if not pts:
        return blocks
    mn, mx = min(pts), max(pts)
    if mn == 1 and mx == v:
        return [tuple(x-1 for x in B) for B in blocks]
    return blocks


def verify_bibd_detailed(v: int,
                         blocks: Iterable[Iterable[int]],
                         k: int = 4,
                         lambd: int = 1,
                         auto_reindex: bool = True) -> Dict[str, Any]:
    rep: Dict[str, Any] = {}
    B = _normalize_blocks(blocks)
    if auto_reindex:
        B = _auto_reindex_if_needed(v, B)
    rep["v"]=v; rep["k_expected"]=k; rep["lambda_expected"]=lambd
    rep["b"]=len(B); rep["blocks_sample"]=B[:5]
    # expected params
    if (lambd*(v-1)) % (k-1) == 0:
        rep["r_expected"] = (lambd*(v-1)) // (k-1)
    else:
        rep["r_expected"] = None
    if rep["r_expected"] is not None and (v*rep["r_expected"]) % k == 0:
        rep["b_expected"] = (v*rep["r_expected"]) // k
    else:
        rep["b_expected"] = None

    # sizes / range
    size_set = set(len(b) for b in B)
    rep["block_sizes_present"]=sorted(size_set)
    rep["size_ok"] = (size_set=={k})
    range_errors=[]
    for b in B:
        for x in b:
            if not (0<=x<v):
                range_errors.append((x,b))
                if len(range_errors)>=5: break
        if range_errors: break
    if range_errors:
        rep["range_errors"]=range_errors

    # replication numbers
    r_count = Counter()
    for b in B:
        for x in b:
            r_count[x]+=1
    rep["r_histogram"]=dict(Counter(r_count.values()).most_common())
    rep["r_values_unique"]=sorted(set(r_count.values()))
    rep["r_empirical_uniform"]= (len(rep["r_values_unique"])==1)
    # deficits (if expected known)
    if rep["r_expected"] is not None:
        deficits = {p: rep["r_expected"]-r_count.get(p,0) for p in range(v)}
        rep["deficit_histogram"]=dict(Counter(deficits.values()).most_common())
        # top under-covered and over-covered
        rep["top_undercovered"]=sorted([ (p,d) for p,d in deficits.items() if d>0 ], key=lambda t:-t[1])[:10]
        rep["top_overcovered"]=sorted([ (p,-d) for p,d in deficits.items() if d<0 ], key=lambda t:-t[1])[:10]
        rep["sum_deficit"]=sum(d for d in deficits.values() if d>0)
        rep["sum_over"]=sum(-d for d in deficits.values() if d<0)
        rep["incident_shortfall_blocks"]=rep["sum_deficit"]/k if rep["sum_deficit"]%k==0 else rep["sum_deficit"]/k
    # identities
    r_emp = next(iter(r_count.values())) if rep["r_empirical_uniform"] else None
    rep["check_vr_eq_bk"] = (v*r_emp == rep["b"]*k) if r_emp is not None else False
    rep["check_param_identity"] = (r_emp*(k-1) == lambd*(v-1)) if r_emp is not None else False

    # pair coverage
    from itertools import combinations
    pair = Counter()
    for b in B:
        for a,b2 in combinations(b,2):
            if a>b2: a,b2=b2,a
            pair[(a,b2)]+=1
    rep["pairs_seen"]=len(pair)
    rep["pairs_expected"]=v*(v-1)//2
    rep["lambda_values_unique"]=sorted(set(pair.values()))
    if rep["pairs_seen"]<rep["pairs_expected"]:
        # report a few missing pairs
        seen=set(pair.keys())
        missing=[]
        got=0
        for a in range(v):
            for b2 in range(a+1,v):
                if (a,b2) not in seen:
                    missing.append((a,b2))
                    got+=1
                    if got>=10: break
            if got>=10: break
        rep["missing_pairs_examples"]=missing

    rep["ok"] = (rep["size_ok"] and
                 rep["r_empirical_uniform"] and
                 rep["lambda_values_unique"]==[lambd] and
                 rep["pairs_seen"]==rep["pairs_expected"] and
                 rep.get("check_vr_eq_bk",False) and
                 rep.get("check_param_identity",False))
    return rep


def summary(rep: Dict[str, Any]) -> str:
    lines=[]
    lines.append(f"BIBD(v={rep.get('v')}, k={rep.get('k_expected')}, λ={rep.get('lambda_expected')})")
    lines.append(f"blocks b={rep.get('b')} (expected {rep.get('b_expected')})")
    lines.append(f"block sizes present: {rep.get('block_sizes_present')}  size_ok={rep.get('size_ok')}")
    if rep.get("r_expected") is not None:
        lines.append(f"r: expected {rep['r_expected']}  histogram {list(rep.get('r_histogram',{}).items())[:5]}")
        lines.append(f"deficit histogram {list(rep.get('deficit_histogram',{}).items())[:5]}  incident shortfall blocks≈{rep.get('incident_shortfall_blocks')}")
    else:
        lines.append(f"r histogram {list(rep.get('r_histogram',{}).items())[:5]}")
    lines.append(f"pair coverage: {rep.get('pairs_seen')}/{rep.get('pairs_expected')} pairs; λ-values present {rep.get('lambda_values_unique')}")
    if rep.get("missing_pairs_examples"):
        lines.append(f"missing pairs examples: {rep['missing_pairs_examples']}")
    lines.append(f"vr=bk? {rep.get('check_vr_eq_bk')} ; r(k-1)=λ(v-1)? {rep.get('check_param_identity')}")
    lines.append(f"OK? {rep.get('ok')}")
    return "\n".join(lines)

if __name__ == '__main__':
    v=361
    blocks = bibd.bibd4(v)
    okrep = verify_bibd_detailed(v, blocks, k=4, lambd=1, auto_reindex=True)
    print(summary(okrep))