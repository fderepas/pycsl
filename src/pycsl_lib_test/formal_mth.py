# Formal tests for pycsl_lib/mth — math module
from pycsl_lib.mth import fabs, floor, ceil, trunc, factorial, max2, min2, comb, perm, remainder


#@ requires x >= 0
#@ ensures \result == x
def test_fabs_identity(x: int) -> int:
    """fabs is identity for non-negative integers."""
    return fabs(x)


#@ requires x >= 0
#@ ensures \result == x
def test_floor_identity(x: int) -> int:
    """floor is identity for integers."""
    return floor(x)


#@ requires x >= 0
#@ ensures \result == x
def test_ceil_identity(x: int) -> int:
    """ceil is identity for integers."""
    return ceil(x)


#@ requires x >= 0
#@ ensures \result == x
def test_trunc_identity(x: int) -> int:
    """trunc is identity for integers."""
    return trunc(x)


#@ requires n >= 0
#@ ensures \result >= 1
def test_factorial_positive(n: int) -> int:
    """n! is always >= 1."""
    return factorial(n)


#@ ensures \result == 1
def test_factorial_zero() -> int:
    """0! == 1."""
    return factorial(0)


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= a
#@ ensures \result >= b
def test_max2_bounds(a: int, b: int) -> int:
    """max2 >= both inputs."""
    return max2(a, b)


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result <= a
#@ ensures \result <= b
def test_min2_bounds(a: int, b: int) -> int:
    """min2 <= both inputs."""
    return min2(a, b)


#@ requires n >= 0
#@ requires k >= 0
#@ requires k <= n
#@ ensures \result >= 1
def test_comb_positive(n: int, k: int) -> int:
    """C(n,k) >= 1."""
    return comb(n, k)


#@ requires x >= 0
#@ requires y > 0
#@ ensures \result >= 0
#@ ensures \result < y
def test_remainder_range(x: int, y: int) -> int:
    """remainder in [0, y)."""
    return remainder(x, y)
