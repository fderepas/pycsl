# pycsl_lib/frac — pure-Python fractions module model
# Named 'frac' to avoid stdlib name clash.
#
# Contracts derived from library_reference/fractions.rst.
# RST: "The fractions module provides support for rational number arithmetic."
# RST: "Fraction(numerator=0, denominator=1)"
#
# Model: Fraction as class with num >= 0, den > 0 (simplified form).

from pycsl_lib.nums import gcd


""  # pycsl
#@ class invariant self._num >= 0
#@ class invariant self._den > 0
class Fraction:
    """RST: 'A Fraction instance can be constructed from a pair of integers.'"""

    def __init__(self):
        self._num = 0
        self._den = 1

    #@ requires num >= 0
    #@ requires den > 0
    #@ ensures self._num >= 0
    #@ ensures self._den > 0
    #@ assigns self._num, self._den
    def set(self, num: int, den: int) -> None:
        """Set numerator and denominator (stores as-is; see normalize)."""
        self._num = num
        self._den = den

    #@ ensures \result >= 0
    #@ ensures \result == self._num
    #@ assigns \nothing
    def numerator(self) -> int:
        """RST: 'Numerator of the Fraction in lowest terms.'"""
        return self._num

    #@ ensures \result > 0
    #@ ensures \result == self._den
    #@ assigns \nothing
    def denominator(self) -> int:
        """RST: 'Denominator of the Fraction in lowest terms.'"""
        return self._den


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result >= 0
def frac_num(num: int, den: int) -> int:
    """Create a fraction and return its numerator.
    Model: returns num (simplified form tracking not modeled)."""
    return num


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result > 0
def frac_den(num: int, den: int) -> int:
    """Create a fraction and return its denominator."""
    return den


#@ requires a_num >= 0
#@ requires a_den > 0
#@ requires b_num >= 0
#@ requires b_den > 0
#@ ensures \result >= 0
#@ assigns \nothing
def frac_add_num(a_num: int, a_den: int, b_num: int, b_den: int) -> int:
    """RST: 'Fraction supports +.' Returns numerator of a + b.
    a/c + b/d = (a*d + b*c) / (c*d). Numerator part."""
    return a_num * b_den + b_num * a_den


#@ requires a_num >= 0
#@ requires a_den > 0
#@ requires b_num >= 0
#@ requires b_den > 0
#@ ensures \result > 0
#@ assigns \nothing
def frac_add_den(a_num: int, a_den: int, b_num: int, b_den: int) -> int:
    """Denominator of a + b = a_den * b_den."""
    return a_den * b_den


#@ requires a_num >= 0
#@ requires a_den > 0
#@ requires b_num >= 0
#@ requires b_den > 0
#@ ensures \result >= 0
#@ assigns \nothing
def frac_mul_num(a_num: int, a_den: int, b_num: int, b_den: int) -> int:
    """RST: 'Fraction supports *.' Numerator of a * b = a_num * b_num."""
    return a_num * b_num


#@ requires a_num >= 0
#@ requires a_den > 0
#@ requires b_num >= 0
#@ requires b_den > 0
#@ ensures \result > 0
#@ assigns \nothing
def frac_mul_den(a_num: int, a_den: int, b_num: int, b_den: int) -> int:
    """Denominator of a * b = a_den * b_den."""
    return a_den * b_den


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result >= 0
#@ ensures \result <= num
#@ assigns \nothing
def frac_floor(num: int, den: int) -> int:
    """RST: 'math.floor(f) — largest int <= f.' = num // den."""
    return num // den


#@ requires num >= 0
#@ requires den > 0
#@ ensures \result >= 0
#@ assigns \nothing
def frac_ceil(num: int, den: int) -> int:
    """RST: 'math.ceil(f) — smallest int >= f.'"""
    return (num + den - 1) // den
