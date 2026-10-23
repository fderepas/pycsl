# Formal tests for pycsl_lib/dec — decimal module
from pycsl_lib.dec import decimal_add, decimal_abs, decimal_remainder, getcontext_prec


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


# (#49) gen #30: `getcontext_prec` gained `requires prec <= 999999999999999999`
# (`decimal.MAX_PREC`; above it the assignment RAISES OverflowError), so this driver must
# discharge it.
#@ requires prec > 0
#@ requires prec <= 999999999999999999
#@ ensures \result > 0
def test_context_prec_pos(prec: int) -> int:
    """Context precision is positive, for a precision CPython accepts."""
    return getcontext_prec(prec)
