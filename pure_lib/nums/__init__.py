# pure_lib/nums — pure-Python numbers module model
# Named 'nums' to avoid stdlib name clash.
#
# Models the numeric tower as abstract contracts.
# Key property: Integral ⊂ Rational ⊂ Real ⊂ Complex ⊂ Number.


#@ requires x >= 0
#@ ensures \result >= 0
def to_int(x: int) -> int:
    """Convert Number to int (truncation). Model: identity."""
    return x


#@ requires x >= 0
#@ requires y > 0
#@ ensures \result >= 0
#@ ensures \result < y
def mod(x: int, y: int) -> int:
    """Modulo operation on integers. Result in [0, y)."""
    return x - (x // y) * y


#@ requires x >= 0
#@ requires y > 0
#@ ensures \result >= 0
def floordiv(x: int, y: int) -> int:
    """Floor division. Result >= 0 for non-negative inputs."""
    return x // y


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result >= 0
def rational_num(num: int, den: int) -> int:
    """Numerator of a rational in lowest terms. Model: num."""
    return num


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result > 0
def rational_den(num: int, den: int) -> int:
    """Denominator of a rational in lowest terms. Model: den."""
    return den


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def gcd(a: int, b: int) -> int:
    """Greatest common divisor. Model: result <= max(a,b)."""
    if a == 0:
        return b
    if b == 0:
        return a
    if a <= b:
        return a
    return b
