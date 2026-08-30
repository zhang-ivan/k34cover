"""Small exact number-theory helpers used by the design constructors.

The active generator only needs three operations that were previously delegated
to SymPy: primality testing, integer factorisation, and irreducibility testing of
small polynomials over prime fields.  Keeping these operations local removes a
large third-party runtime dependency and, in particular, avoids several seconds
of import overhead for the first generated order in the standalone application.

All routines here are deterministic and exact.  For ordinary machine-sized
integers ``is_prime`` uses deterministic Miller--Rabin bases; for larger
integers it falls back to exact trial division rather than silently switching to
probabilistic primality testing.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Dict, Sequence, Tuple


# Deterministic for n < 2**64.
_MR_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def _miller_rabin_witness(a: int, n: int, d: int, s: int) -> bool:
    """Return True if ``a`` proves that odd ``n`` is composite."""
    a %= n
    if a in (0, 1):
        return False
    x = pow(a, d, n)
    if x in (1, n - 1):
        return False
    for _ in range(s - 1):
        x = (x * x) % n
        if x == n - 1:
            return False
    return True


@lru_cache(maxsize=4096)
def is_prime(n: int) -> bool:
    """Return whether ``n`` is prime, deterministically and exactly."""
    n = int(n)
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False

    # n-1 = d*2**s with d odd.
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    if n < (1 << 64):
        return not any(_miller_rabin_witness(a, n, d, s) for a in _MR_BASES_64)

    # Preserve exactness for arbitrary Python integers.  Values this large are
    # far beyond the practical range of the O(v^2) design generator, so a
    # conservative exact fallback is preferable to a probabilistic answer.
    limit = math.isqrt(n)
    candidate = 41
    step = 2
    while candidate <= limit:
        if n % candidate == 0:
            return False
        candidate += step
        step = 6 - step  # 6k-1, 6k+1 progression after 41
    return True


def factorint(n: int) -> Dict[int, int]:
    """Return the exact prime factorisation of ``n`` as ``{prime: exponent}``."""
    n = int(n)
    if n < 2:
        raise ValueError("n must be at least 2")

    factors: Dict[int, int] = {}
    m = n
    for p in (2, 3, 5):
        exponent = 0
        while m % p == 0:
            m //= p
            exponent += 1
        if exponent:
            factors[p] = exponent

    candidate = 7
    step = 4  # 7,11,13,17,19,23,... skips multiples of 2 and 3
    while candidate * candidate <= m:
        exponent = 0
        while m % candidate == 0:
            m //= candidate
            exponent += 1
        if exponent:
            factors[candidate] = exponent
        candidate += step
        step = 6 - step

    if m > 1:
        factors[m] = factors.get(m, 0) + 1
    return factors


# Polynomial helpers use low-to-high coefficients over GF(p).  They are kept
# private because only the finite-field constructor needs them.
def _poly_trim(poly: Sequence[int], p: int) -> Tuple[int, ...]:
    out = [int(c) % p for c in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out or [0])


def _poly_add(a: Sequence[int], b: Sequence[int], p: int) -> Tuple[int, ...]:
    size = max(len(a), len(b))
    return _poly_trim(
        [((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p for i in range(size)],
        p,
    )


def _poly_sub(a: Sequence[int], b: Sequence[int], p: int) -> Tuple[int, ...]:
    size = max(len(a), len(b))
    return _poly_trim(
        [((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p for i in range(size)],
        p,
    )


def _poly_mul(a: Sequence[int], b: Sequence[int], p: int) -> Tuple[int, ...]:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % p
    return _poly_trim(out, p)


def _poly_divmod(
    numerator: Sequence[int], denominator: Sequence[int], p: int
) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    den = _poly_trim(denominator, p)
    if den == (0,):
        raise ZeroDivisionError("polynomial division by zero")
    rem = list(_poly_trim(numerator, p))
    quotient = [0] * max(1, len(rem) - len(den) + 1)
    inv_lead = pow(den[-1], -1, p)
    while len(rem) >= len(den) and any(rem):
        shift = len(rem) - len(den)
        coeff = rem[-1] * inv_lead % p
        quotient[shift] = coeff
        for j, c in enumerate(den):
            rem[shift + j] = (rem[shift + j] - coeff * c) % p
        while len(rem) > 1 and rem[-1] == 0:
            rem.pop()
    return _poly_trim(quotient, p), _poly_trim(rem, p)


def _poly_mod(poly: Sequence[int], modulus: Sequence[int], p: int) -> Tuple[int, ...]:
    return _poly_divmod(poly, modulus, p)[1]


def _poly_gcd(a: Sequence[int], b: Sequence[int], p: int) -> Tuple[int, ...]:
    x = _poly_trim(a, p)
    y = _poly_trim(b, p)
    while y != (0,):
        x, y = y, _poly_mod(x, y, p)
    if x == (0,):
        return x
    inv = pow(x[-1], -1, p)
    return _poly_trim([(c * inv) % p for c in x], p)


def _poly_mul_mod(
    a: Sequence[int], b: Sequence[int], modulus: Sequence[int], p: int
) -> Tuple[int, ...]:
    return _poly_mod(_poly_mul(a, b, p), modulus, p)


def _poly_pow_mod(
    base: Sequence[int], exponent: int, modulus: Sequence[int], p: int
) -> Tuple[int, ...]:
    result: Tuple[int, ...] = (1,)
    power = _poly_mod(base, modulus, p)
    e = int(exponent)
    while e:
        if e & 1:
            result = _poly_mul_mod(result, power, modulus, p)
        power = _poly_mul_mod(power, power, modulus, p)
        e >>= 1
    return result


def is_irreducible_monic(coeffs: Sequence[int], p: int) -> bool:
    """Test a monic polynomial over GF(p) using Rabin's criterion.

    ``coeffs`` are ordered from constant term to leading coefficient.  The
    implementation is exact and is intended for the small degrees occurring in
    the project's finite-field transversal designs.
    """
    f = _poly_trim(coeffs, p)
    degree = len(f) - 1
    if degree < 1 or f[-1] != 1:
        raise ValueError("expected a monic polynomial of positive degree")
    if not is_prime(p):
        raise ValueError(f"p={p} is not prime")
    if degree == 1:
        return True

    x = (0, 1)
    # For every prime divisor q of degree, gcd(x^(p^(d/q))-x, f)=1.
    for q in factorint(degree):
        exponent = p ** (degree // q)
        h = _poly_sub(_poly_pow_mod(x, exponent, f, p), x, p)
        if len(_poly_gcd(f, h, p)) > 1:
            return False

    # And x^(p^d) == x mod f.
    final = _poly_sub(_poly_pow_mod(x, p**degree, f, p), x, p)
    return final == (0,)
