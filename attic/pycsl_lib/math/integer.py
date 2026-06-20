"""PyCSL mock for Python's math.integer module — Integer-specific mathematics functions."""
_ = 0  # anchor

#@ \trusted
#@ requires n >= 0
#@ requires k >= 0
#@ ensures \result >= 0
def comb(n: int, k: int) -> int:
    """Mock: Return the number of ways to choose *k* items from *n* items without repetition and without order. Evaluates to ``n! / (..."""
    return 0

#@ \trusted
#@ requires n >= 0
#@ ensures \result >= 1
def factorial(n: int) -> int:
    """Mock: Return factorial of the nonnegative integer *n*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gcd() -> int:
    """Mock: Return the greatest common divisor of the specified integer arguments. If any of the arguments is nonzero, then the retu..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isqrt(n: int) -> int:
    """Mock: Return the integer square root of the nonnegative integer *n*. This is the floor of the exact square root of *n*, or equ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lcm() -> int:
    """Mock: Return the least common multiple of the specified integer arguments. If all arguments are nonzero, then the returned val..."""
    return 0

#@ \trusted
#@ requires n >= 0
#@ requires k >= 0
#@ ensures \result >= 0
def perm(n: int, k: int) -> int:
    """Mock: Return the number of ways to choose *k* items from *n* items without repetition and with order. Evaluates to ``n! / (n -..."""
    return 0
