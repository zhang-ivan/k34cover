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
