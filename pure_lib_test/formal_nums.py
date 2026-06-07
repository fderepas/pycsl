# Formal test for numbers (nums) module
#
# Based on library_reference/numbers.rst:
#   "The numeric tower: Number > Complex > Real > Rational > Integral"
#
# Tests verify contract postconditions:
#   - mod: 0 <= result < y
#   - floordiv: result >= 0
#   - rational_den: result > 0
#   - gcd: result >= 0

from pure_lib.nums import mod, floordiv, rational_den, gcd


#@ ensures \result >= 0 and \result < 3
def test_mod_range() -> int:
    """mod(7, 3) is in [0, 3)."""
    return mod(7, 3)


#@ ensures \result >= 0
def test_floordiv_nonneg() -> int:
    """floordiv(10, 3) >= 0."""
    return floordiv(10, 3)


#@ ensures \result > 0
def test_rational_den_positive() -> int:
    """Denominator is always positive."""
    return rational_den(3, 7)


#@ ensures \result >= 0
def test_gcd_nonneg() -> int:
    """gcd result is non-negative."""
    return gcd(12, 8)
