# Pure model for decimal — decimal fixed-point arithmetic
# Models Decimal as (sign, coefficient, exponent) triple.
# Arithmetic preserves sign rules and coefficient bounds.

""" # pycsl"""


#@ class invariant self._sign >= 0
#@ class invariant self._sign <= 1
#@ class invariant self._coeff >= 0
class Decimal:
    """Abstract Decimal number: sign * coefficient * 10^exponent."""

    #@ requires sign >= 0
    #@ requires sign <= 1
    #@ requires coeff >= 0
    #@ ensures self._sign == sign
    #@ ensures self._coeff == coeff
    #@ ensures self._exp == exp
    def __init__(self, sign: int, coeff: int, exp: int) -> None:
        self._sign: int = sign
        self._coeff: int = coeff
        self._exp: int = exp

    #@ ensures \result == self._sign
    def sign(self) -> int:
        """Return sign: 0 for positive, 1 for negative."""
        return self._sign

    #@ ensures \result == self._coeff
    def coefficient(self) -> int:
        """Return unsigned coefficient."""
        return self._coeff

    #@ ensures \result == self._exp
    def exponent(self) -> int:
        """Return exponent."""
        return self._exp

    #@ ensures \result >= 0
    def is_zero(self) -> int:
        """Return 1 if value is zero, else 0."""
        if self._coeff == 0:
            return 1
        return 0

    #@ ensures \result >= 0
    #@ ensures \result <= 1
    def is_finite(self) -> int:
        """Return 1 (all modeled decimals are finite)."""
        return 1


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def decimal_add(a: int, b: int) -> int:
    """Add two decimal coefficients."""
    return a + b


#@ requires a >= 0
#@ ensures \result >= 0
def decimal_abs(a: int) -> int:
    """Absolute value of coefficient."""
    return a


#@ requires a >= 0
#@ requires b > 0
#@ ensures \result >= 0
#@ ensures \result < b
def decimal_remainder(a: int, b: int) -> int:
    """Remainder of decimal division."""
    result: int = a % b
    return result


#@ requires prec > 0
#@ ensures \result == prec
def getcontext_prec(prec: int) -> int:
    """Get/set context precision (identity model)."""
    return prec
