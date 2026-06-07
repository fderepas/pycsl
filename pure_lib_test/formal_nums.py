# Formal test for numbers (nums) module
#
# Based on library_reference/numbers.rst:
#   "The root of the numeric hierarchy."
#   Integral supports mod (__mod__) and floordiv (__floordiv__).
#   Rational has .numerator and .denominator properties.
#   gcd(0, b) == b is a standard mathematical identity.

from pure_lib.nums import mod, floordiv, rational_num, rational_den, gcd


#@ ensures \result >= 0 and \result < 3
def test_mod_range() -> int:
    """mod(7, 3) is in [0, 3). Standard modulo semantics."""
    return mod(7, 3)


#@ ensures \result >= 0
def test_floordiv_nonneg() -> int:
    """floordiv(10, 3) >= 0. Non-negative for non-negative inputs."""
    return floordiv(10, 3)


#@ ensures \result == 3
def test_rational_num_exact() -> int:
    """Rational numerator: rational_num(3, 7) == 3."""
    return rational_num(3, 7)


#@ ensures \result > 0
def test_rational_den_positive() -> int:
    """RST: denominator is always positive."""
    return rational_den(3, 7)


#@ ensures \result == 5
def test_gcd_zero_left() -> int:
    """gcd(0, 5) == 5. Mathematical identity: gcd(0, b) = b."""
    return gcd(0, 5)


#@ ensures \result == 12
def test_gcd_zero_right() -> int:
    """gcd(12, 0) == 12. Mathematical identity: gcd(a, 0) = a."""
    return gcd(12, 0)


#@ ensures \result >= 0
def test_gcd_nonneg() -> int:
    """gcd result is always non-negative."""
    return gcd(12, 8)
