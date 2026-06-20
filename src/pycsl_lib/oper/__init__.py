# pycsl_lib/oper — pure-Python operator module model
# Named 'oper' to avoid stdlib name clash.
#
# Contracts derived from library_reference/operator.rst.
# RST: "The operator module exports a set of efficient functions
#  corresponding to the intrinsic operators of Python."
#
# All functions here are pure arithmetic/comparison wrappers.


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == a + b
#@ assigns \nothing
def add(a: int, b: int) -> int:
    """RST: 'Return a + b, for a and b numbers.'"""
    return a + b


#@ requires a >= 0
#@ requires b >= 0
#@ requires a >= b
#@ ensures \result == a - b
#@ assigns \nothing
def sub(a: int, b: int) -> int:
    """RST: 'Return a - b.'"""
    return a - b


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == a * b
#@ ensures \result >= 0
#@ assigns \nothing
def mul(a: int, b: int) -> int:
    """RST: 'Return a * b, for a and b numbers.'"""
    return a * b


#@ requires a >= 0
#@ requires b > 0
#@ ensures \result >= 0
#@ ensures \result == a // b
#@ assigns \nothing
def floordiv(a: int, b: int) -> int:
    """RST: 'Return a // b.'"""
    return a // b


#@ requires a >= 0
#@ requires b > 0
#@ ensures \result >= 0
#@ ensures \result < b
#@ assigns \nothing
def mod(a: int, b: int) -> int:
    """RST: 'Return a % b.'"""
    return a % b


#@ requires x >= 0
#@ ensures \result == x
#@ assigns \nothing
def pos(x: int) -> int:
    """RST: 'Return x positive (unary +).'"""
    return x


#@ requires x >= 0
#@ ensures \result >= 0
#@ ensures \result == x
#@ assigns \nothing
def abs_val(x: int) -> int:
    """RST: 'Return the absolute value of x.' (non-negative input)."""
    return x


#@ requires x >= 0
#@ ensures \result == x
#@ assigns \nothing
def index(x: int) -> int:
    """RST: 'Return x converted to an integer (calls __index__).'"""
    return x


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == 1 or \result == 0
#@ ensures a == b ==> \result == 1
#@ ensures a != b ==> \result == 0
#@ assigns \nothing
def eq(a: int, b: int) -> int:
    """RST: 'Return a == b.' Returns 1 for true, 0 for false."""
    if a == b:
        return 1
    return 0


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == 1 or \result == 0
#@ ensures a != b ==> \result == 1
#@ ensures a == b ==> \result == 0
#@ assigns \nothing
def ne(a: int, b: int) -> int:
    """RST: 'Return a != b.'"""
    if a != b:
        return 1
    return 0


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == 1 or \result == 0
#@ ensures a < b ==> \result == 1
#@ ensures a >= b ==> \result == 0
#@ assigns \nothing
def lt(a: int, b: int) -> int:
    """RST: 'Return a < b.'"""
    if a < b:
        return 1
    return 0


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == 1 or \result == 0
#@ ensures a <= b ==> \result == 1
#@ ensures a > b ==> \result == 0
#@ assigns \nothing
def le(a: int, b: int) -> int:
    """RST: 'Return a <= b.'"""
    if a <= b:
        return 1
    return 0


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == 1 or \result == 0
#@ ensures a > b ==> \result == 1
#@ ensures a <= b ==> \result == 0
#@ assigns \nothing
def gt(a: int, b: int) -> int:
    """RST: 'Return a > b.'"""
    if a > b:
        return 1
    return 0


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == 1 or \result == 0
#@ ensures a >= b ==> \result == 1
#@ ensures a < b ==> \result == 0
#@ assigns \nothing
def ge(a: int, b: int) -> int:
    """RST: 'Return a >= b.'"""
    if a >= b:
        return 1
    return 0


#@ requires \length(seq) > 0
#@ requires idx >= 0
#@ requires idx < \length(seq)
#@ assigns \nothing
def getitem(seq: list, idx: int) -> int:
    """RST: 'Return the value of seq at index idx.'"""
    return seq[idx]


#@ requires \length(seq) > 0
#@ requires idx >= 0
#@ requires idx < \length(seq)
#@ assigns seq[idx]
def setitem(seq: list, idx: int, val: int) -> None:
    """RST: 'Set the value of seq at index idx to val.'"""
    seq[idx] = val


#@ requires \length(seq) >= 0
#@ ensures \result == \length(seq)
#@ assigns \nothing
def length_hint(seq: list) -> int:
    """RST: 'Return an estimated length for the object.'
    Exact for sequences."""
    return len(seq)
