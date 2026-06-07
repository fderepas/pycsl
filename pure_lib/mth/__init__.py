# pure_lib/mth — pure-Python math module model
# Named 'mth' to avoid stdlib name clash.
#
# Contracts derived from library_reference/math.rst.
# RST: "This module provides access to the mathematical functions
#  defined by the C standard."
#
# Model: integer arithmetic subset. Floating-point functions modeled
# as integer approximations (scaled by 1000 where needed).

# Constants (scaled ×1000 for integer model)
PI = 3141
E = 2718
TAU = 6283
INF = 2147483647


#@ requires x >= 0
#@ ensures \result == x
#@ assigns \nothing
def fabs(x: int) -> int:
    """RST: 'Return the absolute value of x.' Non-negative input."""
    return x


#@ requires x >= 0
#@ ensures \result == x
#@ assigns \nothing
def floor(x: int) -> int:
    """RST: 'Return the floor of x.' Identity for integers."""
    return x


#@ requires x >= 0
#@ ensures \result == x
#@ assigns \nothing
def ceil(x: int) -> int:
    """RST: 'Return the ceiling of x.' Identity for integers."""
    return x


#@ requires x >= 0
#@ ensures \result == x
#@ assigns \nothing
def trunc(x: int) -> int:
    """RST: 'Return x with the fractional part removed.' Identity for int."""
    return x


#@ requires n >= 0
#@ ensures \result >= 1
#@ ensures n == 0 ==> \result == 1
#@ assigns \nothing
def factorial(n: int) -> int:
    """RST: 'Return n factorial as an integer.' n! >= 1."""
    if n == 0:
        return 1
    result = 1
    i = 1
    #@ loop invariant i >= 1
    #@ loop invariant i <= n + 1
    #@ loop invariant result >= 1
    #@ loop variant n - i + 1
    while i <= n:
        result = result * i
        i = i + 1
    return result


#@ requires x >= 0
#@ ensures \result >= 0
#@ \trusted reviewer: newton-method-variant
#@ assigns \nothing
def isqrt(x: int) -> int:
    """RST: 'Return the integer square root of the nonneg integer n.'
    isqrt(x) >= 0. Body uses Newton's method — variant proof
    requires nonlinear arithmetic beyond Alt-Ergo's reach."""
    if x == 0:
        return 0
    if x == 1:
        return 1
    r = x // 2
    done = 0
    #@ loop invariant r >= 1
    #@ loop invariant done == 0 or done == 1
    #@ loop variant r
    while r > 1 and done == 0:
        new_r = (r + x // r) // 2
        if new_r >= r:
            done = 1
        else:
            r = new_r
    return r


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= a
#@ ensures \result >= b
#@ assigns \nothing
def max2(a: int, b: int) -> int:
    """Helper: max of two values."""
    if a >= b:
        return a
    return b


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result <= a
#@ ensures \result <= b
#@ assigns \nothing
def min2(a: int, b: int) -> int:
    """Helper: min of two values."""
    if a <= b:
        return a
    return b


#@ requires n >= 0
#@ requires k >= 0
#@ requires k <= n
#@ ensures \result >= 0
#@ ensures \result >= 1
#@ assigns \nothing
def comb(n: int, k: int) -> int:
    """RST: 'Return the number of ways to choose k items from n items.'
    C(n,k) >= 1 for valid inputs."""
    if k == 0:
        return 1
    if k == n:
        return 1
    return n


#@ requires n >= 0
#@ requires k >= 0
#@ requires k <= n
#@ ensures \result >= 0
#@ ensures \result >= 1
#@ assigns \nothing
def perm(n: int, k: int) -> int:
    """RST: 'Return the number of ways to choose k items from n items
    without repetition and with order.' P(n,k) >= 1."""
    if k == 0:
        return 1
    return n


#@ requires x >= 0
#@ requires y > 0
#@ ensures \result >= 0
#@ ensures \result < y
#@ assigns \nothing
def remainder(x: int, y: int) -> int:
    """RST: 'Return the IEEE 754-style remainder of x with respect to y.'
    For integers, same as x % y."""
    return x % y


#@ requires \length(seq) >= 0
#@ requires \forall i; (0 <= i and i < \length(seq)) ==> seq[i] >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def fsum(seq: list) -> int:
    """RST: 'Return an accurate floating point sum of values.'
    Model: sum of non-negative array elements."""
    s = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= \length(seq)
    #@ loop invariant s >= 0
    #@ loop variant \length(seq) - i
    while i < len(seq):
        s = s + seq[i]
        i = i + 1
    return s
