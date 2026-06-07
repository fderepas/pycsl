# Formal test for numbers (nums) module — universally quantified
#
# Based on library_reference/numbers.rst:
#   "The root of the numeric hierarchy."
#   Integral supports mod (__mod__) and floordiv (__floordiv__).
#   Rational has .numerator and .denominator properties.
#   gcd(0, b) == b is a standard mathematical identity.

from pure_lib.nums import mod, floordiv, rational_num, rational_den, gcd


#@ requires x >= 0 and x < 2147483647
#@ requires y > 0 and y < 2147483647
#@ ensures \result >= 0 and \result < y
def test_mod_range(x: int, y: int) -> int:
    """mod(x, y) is in [0, y) for all valid x, y."""
    return mod(x, y)


#@ requires x >= 0 and x < 2147483647
#@ requires y > 0 and y < 2147483647
#@ ensures \result >= 0
def test_floordiv_nonneg(x: int, y: int) -> int:
    """floordiv(x, y) >= 0 for all non-negative x and positive y."""
    return floordiv(x, y)


#@ requires num >= 0 and num < 2147483647
#@ requires den > 0 and den < 2147483647
#@ ensures \result == num
def test_rational_num(num: int, den: int) -> int:
    """rational_num(num, den) == num for all valid inputs."""
    return rational_num(num, den)


#@ requires num >= 0 and num < 2147483647
#@ requires den > 0 and den < 2147483647
#@ ensures \result == den
def test_rational_den(num: int, den: int) -> int:
    """rational_den(num, den) == den (always positive) for all valid inputs."""
    return rational_den(num, den)


#@ requires b >= 0 and b < 2147483647
#@ ensures \result == b
def test_gcd_zero_left(b: int) -> int:
    """gcd(0, b) == b for all b >= 0. Mathematical identity."""
    return gcd(0, b)


#@ requires a >= 0 and a < 2147483647
#@ ensures \result == a
def test_gcd_zero_right(a: int) -> int:
    """gcd(a, 0) == a for all a >= 0. Mathematical identity."""
    return gcd(a, 0)


#@ requires a >= 0 and a < 2147483647
#@ requires b >= 0 and b < 2147483647
#@ ensures \result >= 0
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
def test_gcd_nonneg(a: int, b: int) -> int:
    """gcd(a, b) divides both a and b for all a, b >= 0."""
    return gcd(a, b)
