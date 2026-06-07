# Formal tests for pure_lib/dec — decimal module
from pure_lib.dec import decimal_add, decimal_abs, decimal_remainder, getcontext_prec


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def test_add_nonneg(a: int, b: int) -> int:
    """Decimal add of non-negatives is non-negative."""
    return decimal_add(a, b)


#@ requires a >= 0
#@ ensures \result >= 0
def test_abs_nonneg(a: int) -> int:
    """Absolute value is non-negative."""
    return decimal_abs(a)


#@ requires a >= 0
#@ requires b > 0
#@ ensures \result >= 0
def test_remainder_nonneg(a: int, b: int) -> int:
    """Remainder is non-negative."""
    return decimal_remainder(a, b)


#@ requires prec > 0
#@ ensures \result > 0
def test_context_prec_pos(prec: int) -> int:
    """Context precision is positive."""
    return getcontext_prec(prec)
