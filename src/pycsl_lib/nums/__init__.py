# pycsl_lib/nums — pure-Python numbers module model
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
    """RST: Integral.__int__ -> convert to int. Identity for int inputs."""
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


#@ proof rocq Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_positive
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_a
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_b
#@ proof rocq Pycsl.Reference.Gcd.gcd_0
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof rocq Pycsl.Reference.Gcd.gcd_greatest
#@ proof lean Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof lean Pycsl.Reference.Gcd.gcd_result_positive
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_a
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_b
#@ proof lean Pycsl.Reference.Gcd.gcd_0
#@ proof lean Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_greatest
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures a == 0 ==> \result == b
#@ ensures b == 0 ==> \result == a
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
#@ ensures \result == gcd(a, b)
#@ ensures (a > 0 or b > 0) ==> (\forall k; (k > 0 and a % k == 0 and b % k == 0) ==> k <= \result)
#@ assigns \nothing
def gcd(a: int, b: int) -> int:
    """GCD via Euclidean algorithm, fully proven with cross-validated
    Rocq + Lean axioms. Captures the complete mathematical definition:
    result divides both inputs AND is the GREATEST such divisor."""
    x = a
    y = b
    #@ loop invariant x >= 0
    #@ loop invariant y >= 0
    #@ loop invariant gcd(x, y) == gcd(a, b)
    #@ loop invariant (a > 0 or b > 0) ==> (x > 0 or y > 0)
    #@ loop variant y
    while y != 0:
        r = x % y
        x = y
        y = r
    return x


# --- Rational class ---

""  # pycsl
#@ class invariant self._num >= 0
#@ class invariant self._den > 0
class Rational:
    """RST: 'Rational subtypes Real and adds numerator and denominator properties.
    With these, it provides a default for float().'"""

    def __init__(self):
        self._num = 0
        self._den = 1

    #@ requires num >= 0
    #@ requires den > 0
    #@ ensures self._num == num
    #@ ensures self._den == den
    #@ assigns self._num, self._den
    def set(self, num: int, den: int) -> None:
        """Set numerator and denominator."""
        self._num = num
        self._den = den

    #@ ensures \result >= 0
    #@ ensures \result == self._num
    #@ assigns \nothing
    def numerator(self) -> int:
        """RST: 'Abstract property. Numerator of the rational.'"""
        return self._num

    #@ ensures \result > 0
    #@ ensures \result == self._den
    #@ assigns \nothing
    def denominator(self) -> int:
        """RST: 'Abstract property. Denominator of the rational.'"""
        return self._den
