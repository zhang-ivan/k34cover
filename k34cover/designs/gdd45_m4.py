from collections import Counter

import k34cover.designs.transversal as transversal
# from k34cover.designs.r_picker import pick_r_mod01_pp4 as r_picker

def _min_prime_power_factor(n: int) -> int:
    """
    Return min_{p^e || n} p^e, i.e., the smallest exact prime-power factor of n.
    Examples:
      21 = 3^1·7^1 -> 3
      12 = 2^2·3^1 -> min(4,3) = 3
      20 = 2^2·5^1 -> min(4,5) = 4
    """
    assert n >= 2
    min_pp = float('inf')

    # factor 2
    e = 0
    m = n
    while m % 2 == 0:
        m //= 2
        e += 1
    if e > 0:
        min_pp = min(min_pp, 2 ** e)

    # factor odd primes
    p = 3
    while p * p <= m:
        e = 0
        while m % p == 0:
            m //= p
            e += 1
        if e > 0:
            min_pp = min(min_pp, p ** e)
        p += 2

    # leftover prime
    if m > 1:
        min_pp = min(min_pp, m)

    return int(min_pp)

def _is_valid_r(r: int) -> bool:
    """r valid iff r % 4 in {0,1} and smallest prime-power factor >= 4."""
    if r % 4 not in (0, 1):
        return False
    if r < 2:
        return False
    return _min_prime_power_factor(r) >= 4

def pick_r_mod01_pp4(u: int) -> int:
    """
    Used in Lemma 5.8
    Choose the largest r in [ceil(u/5), floor(u/4)] such that:
      - r ≡ 0 or 1 (mod 4),
      - smallest exact prime-power factor of r >= 4,
      - 0 ≤ r1 = u - 4r ≤ r.
    Assumes u ≥ 52 and u ≡ 0 or 1 (mod 4).
    """
    assert u >= 52 and u % 4 in (0, 1), f"u={u} must be 0/1 (mod 4)"
    l = (u + 4) // 5   # ceil(u/5)
    h = u // 4         # floor(u/4)

    for r in range(h, l - 1, -1):  # descend to reduce u fastest
        if not _is_valid_r(r):
            continue
        u1 = u - 4 * r
        if 0 <= u1 <= r:
            return r

    raise ValueError(
        f"No valid r in [{l},{h}] for u={u} with r≡0/1 (mod 4) and min prime-power factor ≥ 4."
    )


M4 = {1, 4, 5, 8, 9, 12, 13, 28, 29}

def _verify_gdd_45_m4(u, blocks, groups, verbose=True):
    ok = True
    msgs = []

    # 1) partition check
    cover = set(x for G in groups for x in G)
    need  = set(range(1, u+1))
    if cover != need:
        ok = False
        msgs.append(f"Groups do not partition 1..{u}; missing={sorted(need-cover)[:10]} extra={sorted(cover-need)[:10]}")

    # 2) group-size ∈ M4
    gsz = [len(G) for G in groups]
    bad_sizes = [s for s in gsz if s not in M4]
    if bad_sizes:
        ok = False
        msgs.append(f"Group sizes not all in M4; bad={sorted(Counter(bad_sizes).items())} ; sizes={gsz}")

    # 3) block sizes {4,5}
    bsz = [len(B) for B in blocks]
    if set(bsz) - {4,5}:
        ok = False
        msgs.append(f"Blocks have sizes outside {{4,5}}; histogram={sorted(Counter(bsz).items())}")

    # 4) no block has two points from same group
    p2g = {}
    for i,G in enumerate(groups):
        for x in G: p2g[x]=i
    for B in blocks:
        if any(p2g[a]==p2g[b] for i,a in enumerate(B) for b in B[i+1:]):
            ok = False
            msgs.append(f"Block {B} contains two points from the same group")
            break

    # 5) λ=1 on cross-group pairs
    seen = set()
    for B in blocks:
        bb = sorted(B)
        for i in range(len(bb)):
            for j in range(i+1,len(bb)):
                a,b = bb[i], bb[j]
                if p2g[a]==p2g[b]:  # same-group pairs should NOT appear
                    continue
                key = (a,b)
                if key in seen:
                    ok = False
                    msgs.append(f"Pair {key} occurs more than once across groups")
                    break
                seen.add(key)
        if not ok: break

    # expected cross-pair count
    exp_pairs = sum(len(A)*len(B) for i,A in enumerate(groups) for j,B in enumerate(groups) if i<j)
    if len(seen) != exp_pairs:
        ok = False
        msgs.append(f"Cross-group pair count mismatch: got={len(seen)} expected={exp_pairs}")

    if verbose:
        print(f"GDD(4,5,M4) check: u={u}  b={len(blocks)}")
        print(f"  group sizes: {gsz}")
        print(f"  block-size histogram: {sorted(Counter(bsz).items())}")
        print(f"  cross-pairs covered: {len(seen)}/{exp_pairs}")
        print("  OK?" , ok)
        if not ok:
            for m in msgs[:5]:
                print("  -", m)
    return ok, msgs


def u45(u, design=None, groups=None, enforce_mod: bool = True):  # Intermediate design {4,5}-GDD of order u and groups in M4
    """Lemma 5.8"""
    u = int(u)
    if groups is None:
        groups = []
    if design is None:
        design = []
    if enforce_mod:
        assert u % 4 in (0, 1), f"input {u} is not congruent to 0 or 1 (mod 4)!"

    # print(f"[u45] ENTER u={u}")

    if u in M4:
        groups.append(tuple(range(1, u + 1)))

    elif u in [16, 17, 20]:
        # print(f"[u45] small case {u} via trans1(2,2)")
        design = transversal.truncate(transversal.trans1(2, 2), u - 16)
        groups.extend([(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 16)])
        if u > 16:
            groups.append(tuple(range(17, u + 1)))


    elif u in [21, 24, 25]:
        # print(f"[u45] small case {u} via trans1(5,1) + trim")
        design = transversal.truncate(transversal.trans_trim(transversal.trans1(5, 1), 5), u - 20)
        groups.extend([(1, 2, 3, 4, 5), (6, 7, 8, 9, 10), (11, 12, 13, 14, 15), (16, 17, 18, 19, 20)])
        groups.append(tuple(range(21, u + 1)))

    elif u in [32, 33, 36, 37, 40]:
        # print(f"[u45] small case {u} via trans1(2,3) + trim")
        design = transversal.truncate(transversal.trans_trim(transversal.trans1(2, 3), 5), u - 32)
        groups.extend([tuple(range(1, 9)), tuple(range(9, 17)), tuple(range(17, 25)), tuple(range(25, 33))])
        if u > 32:
            groups.append(tuple(range(33, u + 1)))

    elif u in [41, 44, 45]:
        # print(f"[u45] small case {u} via trans1(3,2) + trim")
        design = transversal.truncate(transversal.trans_trim(transversal.trans1(3, 2), 5), u - 36)
        groups.extend([tuple(range(1, 10)), tuple(range(10, 19)), tuple(range(19, 28)), tuple(range(28, 37))])
        groups.append(tuple(range(37, u + 1)))

    elif u in [48, 49]:
        # print(f"[u45] small case {u} via explicit 6×2 structure + trim")
        gdd6_12_6 = []
        for i in range(6):
            for j in range(2):
                block_tmp = [2 * i + j + 1, 12 + 2 * i + j + 1, 24 + 2 * i + j + 1, 36 + 2 * i + j + 1,
                             48 + 2 * i + j + 1, 60 + 2 * i + j + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * ((i + 1) % 6) + j + 1, 24 + 2 * i + (j + 1) % 2 + 1,
                             36 + 2 * ((i + 3) % 6) + j + 1, 48 + 2 * ((i + 2) % 6) + (j + 1) % 2 + 1,
                             60 + 2 * ((i + 4) % 6) + j + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * ((i + 2) % 6) + j + 1, 24 + 2 * ((i + 2) % 6) + (j + 1) % 2 + 1,
                             36 + 2 * i + (j + 1) % 2 + 1, 48 + 2 * ((i + 1) % 6) + j + 1,
                             60 + 2 * ((i + 5) % 6) + (j + 1) % 2 + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * ((i + 3) % 6) + j + 1, 24 + 2 * ((i + 2) % 6) + j + 1,
                             36 + 2 * ((i + 1) % 6) + j + 1, 48 + 2 * ((i + 5) % 6) + (j + 1) % 2 + 1,
                             60 + 2 * ((i + 4) % 6) + (j + 1) % 2 + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * ((i + 4) % 6) + j + 1, 24 + 2 * ((i + 1) % 6) + (j + 1) % 2 + 1,
                             36 + 2 * ((i + 3) % 6) + (j + 1) % 2 + 1, 48 + 2 * ((i + 5) % 6) + j + 1,
                             60 + 2 * ((i + 2) % 6) + j + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * ((i + 5) % 6) + j + 1, 24 + 2 * ((i + 1) % 6) + j + 1,
                             36 + 2 * ((i + 5) % 6) + (j + 1) % 2 + 1, 48 + 2 * ((i + 3) % 6) + (j + 1) % 2 + 1,
                             60 + 2 * ((i + 1) % 6) + (j + 1) % 2 + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * i + (j + 1) % 2 + 1, 24 + 2 * ((i + 3) % 6) + (j + 1) % 2 + 1,
                             36 + 2 * ((i + 2) % 6) + j + 1, 48 + 2 * ((i + 3) % 6) + j + 1,
                             60 + 2 * ((i + 2) % 6) + (j + 1) % 2 + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * ((i + 1) % 6) + (j + 1) % 2 + 1,
                             24 + 2 * ((i + 5) % 6) + (j + 1) % 2 + 1,
                             36 + 2 * ((i + 2) % 6) + (j + 1) % 2 + 1, 48 + 2 * ((i + 4) % 6) + (j + 1) % 2 + 1,
                             60 + 2 * i + (j + 1) % 2 + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * ((i + 2) % 6) + (j + 1) % 2 + 1, 24 + 2 * ((i + 4) % 6) + j + 1,
                             36 + 2 * ((i + 5) % 6) + j + 1, 48 + 2 * ((i + 2) % 6) + j + 1,
                             60 + 2 * ((i + 3) % 6) + (j + 1) % 2 + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * ((i + 3) % 6) + (j + 1) % 2 + 1,
                             24 + 2 * ((i + 4) % 6) + (j + 1) % 2 + 1,
                             36 + 2 * ((i + 4) % 6) + j + 1, 48 + 2 * ((i + 1) % 6) + (j + 1) % 2 + 1,
                             60 + 2 * ((i + 1) % 6) + j + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * ((i + 4) % 6) + (j + 1) % 2 + 1, 24 + 2 * ((i + 5) % 6) + j + 1,
                             36 + 2 * ((i + 1) % 6) + (j + 1) % 2 + 1, 48 + 2 * i + (j + 1) % 2 + 1,
                             60 + 2 * ((i + 3) % 6) + j + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2 * i + j + 1, 12 + 2 * ((i + 5) % 6) + (j + 1) % 2 + 1, 24 + 2 * ((i + 3) % 6) + j + 1,
                             36 + 2 * ((i + 4) % 6) + (j + 1) % 2 + 1, 48 + 2 * ((i + 4) % 6) + j + 1,
                             60 + 2 * ((i + 5) % 6) + j + 1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                gdd6_12_6 = sorted(gdd6_12_6)
        gdd5_12_5 = transversal.trans_trim(gdd6_12_6, 5)
        design = transversal.truncate(gdd5_12_5, u - 48)
        groups.extend([tuple(range(1, 13)), tuple(range(13, 25)), tuple(range(25, 37)), tuple(range(37, 49))])
        if u > 48:
            groups.append(tuple(range(49, u + 1)))

    elif u>=52:
        # L,H = _window(u)
        # print(f"[u45] u>=52 branch. window r∈[{L},{H}]")
        r = pick_r_mod01_pp4(u)
        r1 = u-4*r
        # print(f"[u45] picked r={r} (r%4={r%4}); r1=u-4r={r1} (r∈M4? {r in M4}, r1∈M4? {r1 in M4})")
        assert 0 <= r1 <= r, f"[u45] sanity fail: r1={r1} not in [0,r] with r={r}"

        # TD build
        trans_full = transversal.trans2(r)

        # Trim to 5 columns (harmless if already 5)
        design = transversal.trans_trim(trans_full, 5)

        # Four contiguous groups of size r
        g_before = [
            tuple(range(1,r+1)),
            tuple(range(r+1,2*r+1)),
            tuple(range(2*r+1,3*r+1)),
            tuple(range(3*r+1,4*r+1)),
        ]
        groups.extend(g_before)

        if r1 < r:
            # print(f"[u45] truncating 5th column from {r} → r1={r1}")
            design = transversal.truncate(design, r1)
        # else:
            # print(f"[u45] no truncation needed (r1==r)")

        # Add the (possibly empty) 5th group
        if r1 > 0:
            fifth = tuple(range(4*r+1,4*r+r1+1))
            groups.append(fifth)
            # print(f"[u45] appended 5th group size={len(fifth)}  interval=[{4*r+1},{4*r+r1}]")
            if r1 not in M4:
                # print(f"[u45] RECURSE into r1={r1} (not in M4)")
                subdesign, subgroups = u45(r1)
                left = 4*r+1
                # shift subdesign/subgroups to the 5th group's label range
                shifted_subdesign = [tuple(x + left - 1 for x in t) for t in subdesign]
                shifted_subgroups = [tuple(x + left - 1 for x in t) for t in subgroups]
                # replace the single 5th group by its refined subgroups
                groups[-1:] = shifted_subgroups
                design.extend(shifted_subdesign)

        # Now handle the 4 big columns if r not in M4
        if r not in M4:
            # print(f"[u45] RECURSE into r={r} for each of 4 columns (since r∉M4)")
            subdesign, subgroups = u45(r)

            for i in range(0, 4):
                left = i*r+1
                right = (i+1)*r
                # shift to the i-th column’s label interval
                shifted_subdesign = [tuple(x+left-1 for x in t) for t in subdesign]
                shifted_subgroups = [tuple(x + left - 1 for x in t) for t in subgroups]
                # find and replace the old column group interval
                old = tuple(range(left, right+1))
                try:
                    old_index = groups.index(old)
                except ValueError:
                    print(f"[u45][WARN] could not find old group interval [{left},{right}] to replace!")
                    old_index = None
                if old_index is not None:
                    groups[old_index:old_index+1] = shifted_subgroups
                design.extend(shifted_subdesign)
                # print(f"[u45] column {i}: replaced [{left},{right}] with {len(shifted_subgroups)} groups; added {len(shifted_subdesign)} blocks.")
    return design, groups



if __name__ == '__main__':


    for u in range(0,400):
        if u % 4 in [0, 1]:
            print("\n=== u =", u, "===")
            design, groups = u45(u)
            ok, msgs = _verify_gdd_45_m4(u, design, groups)