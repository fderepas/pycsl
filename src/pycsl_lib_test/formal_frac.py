# Formal tests for pycsl_lib/frac — fractions module
from pycsl_lib.frac import frac_num, frac_den, frac_add_num, frac_add_den, frac_mul_num, frac_mul_den, frac_floor, frac_ceil


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result >= 0
def test_frac_num_nonneg(num: int, den: int) -> int:
    """Fraction numerator is non-negative."""
    return frac_num(num, den)


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result > 0
def test_frac_den_positive(num: int, den: int) -> int:
    """Fraction denominator is positive."""
    return frac_den(num, den)


#@ requires a_num >= 0
#@ requires a_den > 0
#@ requires b_num >= 0
#@ requires b_den > 0
#@ ensures \result >= 0
def test_frac_add_nonneg(a_num: int, a_den: int, b_num: int, b_den: int) -> int:
    """Sum of non-negative fractions has non-negative numerator."""
    return frac_add_num(a_num, a_den, b_num, b_den)


#@ requires a_num >= 0
#@ requires a_den > 0
#@ requires b_num >= 0
#@ requires b_den > 0
#@ ensures \result > 0
def test_frac_add_den_positive(a_num: int, a_den: int, b_num: int, b_den: int) -> int:
    """Sum denominator is always positive."""
    return frac_add_den(a_num, a_den, b_num, b_den)


#@ requires a_num >= 0
#@ requires a_den > 0
#@ requires b_num >= 0
#@ requires b_den > 0
#@ ensures \result >= 0
def test_frac_mul_nonneg(a_num: int, a_den: int, b_num: int, b_den: int) -> int:
    """Product numerator is non-negative."""
    return frac_mul_num(a_num, a_den, b_num, b_den)


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result >= 0
#@ ensures \result <= num
def test_frac_floor_bounded(num: int, den: int) -> int:
    """floor(num/den) <= num."""
    return frac_floor(num, den)
