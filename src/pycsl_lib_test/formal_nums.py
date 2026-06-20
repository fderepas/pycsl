# Formal tests for pycsl_lib/nums — numbers module model
from pycsl_lib.nums import to_int, mod, floordiv, rational_num, rational_den, gcd


#@ requires x >= 0
#@ ensures \result == x
def test_to_int_identity(x: int) -> int:
    """Integral.__int__ is identity for int inputs."""
    return to_int(x)


#@ requires x >= 0
#@ requires y > 0
#@ ensures \result >= 0
#@ ensures \result < y
def test_mod_range(x: int, y: int) -> int:
    """mod result in [0, y)."""
    return mod(x, y)


#@ requires x >= 0
#@ requires y > 0
#@ ensures \result >= 0
def test_floordiv_nonneg(x: int, y: int) -> int:
    """floordiv non-negative for non-negative inputs."""
    return floordiv(x, y)


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result == num
def test_rational_num_value(num: int, den: int) -> int:
    """Rational.numerator returns num."""
    return rational_num(num, den)


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result == den
def test_rational_den_value(num: int, den: int) -> int:
    """Rational.denominator returns den."""
    return rational_den(num, den)


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures a == 0 ==> \result == b
#@ ensures b == 0 ==> \result == a
def test_gcd_base_cases(a: int, b: int) -> int:
    """GCD base: gcd(a,0)=a, gcd(0,b)=b."""
    return gcd(a, b)
