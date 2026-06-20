# Formal tests for pycsl_lib/oper — operator module
from pycsl_lib.oper import add, sub, mul, floordiv, mod, eq, ne, lt, le, gt, ge


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == a + b
def test_add_correct(a: int, b: int) -> int:
    """add(a,b) == a + b."""
    return add(a, b)


#@ requires a >= 0
#@ requires b >= 0
#@ requires a >= b
#@ ensures \result == a - b
def test_sub_correct(a: int, b: int) -> int:
    """sub(a,b) == a - b."""
    return sub(a, b)


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == a * b
def test_mul_correct(a: int, b: int) -> int:
    """mul(a,b) == a * b."""
    return mul(a, b)


#@ requires a >= 0
#@ requires b > 0
#@ ensures \result == a // b
def test_floordiv_correct(a: int, b: int) -> int:
    """floordiv(a,b) == a // b."""
    return floordiv(a, b)


#@ requires a >= 0
#@ requires b > 0
#@ ensures \result >= 0
#@ ensures \result < b
def test_mod_range(a: int, b: int) -> int:
    """mod(a,b) is in [0, b)."""
    return mod(a, b)


#@ requires a >= 0
#@ requires b >= 0
#@ ensures a == b ==> \result == 1
#@ ensures a != b ==> \result == 0
def test_eq_correct(a: int, b: int) -> int:
    """eq returns 1 iff equal."""
    return eq(a, b)


#@ requires a >= 0
#@ requires b >= 0
#@ ensures a < b ==> \result == 1
#@ ensures a >= b ==> \result == 0
def test_lt_correct(a: int, b: int) -> int:
    """lt returns 1 iff a < b."""
    return lt(a, b)
