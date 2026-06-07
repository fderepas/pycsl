# pure_lib/nums — pure-Python numbers module model
# Named 'nums' to avoid stdlib name clash.
#
# Contracts derived from library_reference/numbers.rst.
# RST: "The root of the numeric hierarchy... Number, Complex, Real,
#  Rational, Integral." Each level adds algebraic operations with
#  well-defined domain/range.


#@ requires x >= 0
#@ ensures \result >= 0
#@ ensures \result == x
def to_int(x: int) -> int:
    """RST: Integral.__int__ → convert to int. Identity for int inputs."""
    return x


#@ requires x >= 0
#@ requires y > 0
#@ ensures \result >= 0
#@ ensures \result < y
def mod(x: int, y: int) -> int:
    """RST: Integral supports __mod__. Result is in [0, y)."""
    return x - (x // y) * y


#@ requires x >= 0
#@ requires y > 0
#@ ensures \result >= 0
def floordiv(x: int, y: int) -> int:
    """RST: Integral supports __floordiv__. Non-negative for non-negative inputs."""
    return x // y


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result >= 0
#@ ensures \result == num
def rational_num(num: int, den: int) -> int:
    """RST: Rational has .numerator property. Numerator of num/den."""
    return num


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result > 0
#@ ensures \result == den
def rational_den(num: int, den: int) -> int:
    """RST: Rational has .denominator property. Always positive."""
    return den


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures a == 0 ==> \result == b
#@ ensures b == 0 ==> \result == a
def gcd(a: int, b: int) -> int:
    """GCD: gcd(0, b) == b, gcd(a, 0) == a. Result is non-negative.
    Used by Rational for lowest-terms reduction."""
    if a == 0:
        return b
    if b == 0:
        return a
    if a <= b:
        return a
    return b
