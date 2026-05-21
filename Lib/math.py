"""PyCSL mock for Python's math module — Mathematical functions (sin() etc.)."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= x
def ceil(x: int) -> int:
    """Mock: Return the ceiling of *x*, the smallest integer greater than or equal to *x*. If *x* is not a float, delegates to :meth:..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fabs(x: int) -> int:
    """Mock: Return the absolute value of *x*."""
    return 0

#@ \trusted
#@ ensures \result <= x
def floor(x: int) -> int:
    """Mock: Return the floor of *x*, the largest integer less than or equal to *x*.  If *x* is not a float, delegates to :meth:`x.__..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fma(x: int, y: int, z: int) -> int:
    """Mock: Fused multiply-add operation. Return ``(x * y) + z``, computed as though with infinite precision and range followed by a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fmax(x: int, y: int) -> int:
    """Mock: Get the larger of two floating-point values, treating NaNs as missing data. When both operands are (signed) NaNs or zero..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fmin(x: int, y: int) -> int:
    """Mock: Get the smaller of two floating-point values, treating NaNs as missing data. When both operands are (signed) NaNs or zer..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fmod(x: int, y: int) -> int:
    """Mock: Return the floating-point remainder of ``x / y``, as defined by the platform C library function ``fmod(x, y)``. Note tha..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def modf(x: int) -> int:
    """Mock: Return the fractional and integer parts of *x*.  Both results carry the sign of *x* and are floats. Note that :func:`mod..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def remainder(x: int, y: int) -> int:
    """Mock: Return the IEEE 754-style remainder of *x* with respect to *y*.  For finite *x* and finite nonzero *y*, this is the diff..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def trunc(x: int) -> int:
    """Mock: Return *x* with the fractional part removed, leaving the integer part.  This rounds toward 0: ``trunc()`` is equivalent ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copysign(x: int, y: int) -> int:
    """Mock: Return a float with the magnitude (absolute value) of *x* but the sign of *y*.  On platforms that support signed zeros, ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def frexp(x: int) -> int:
    """Mock: Return the mantissa and exponent of *x* as the pair ``(m, e)``.  *m* is a float and *e* is an integer such that ``x == m..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isclose(a: int, b: int, rel_tol: int, abs_tol: int) -> int:
    """Mock: Return ``True`` if the values *a* and *b* are close to each other and ``False`` otherwise. Whether or not two values are..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isfinite(x: int) -> int:
    """Mock: Return ``True`` if *x* is neither an infinity nor a NaN, and ``False`` otherwise.  (Note that ``0.0`` *is* considered fi..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isnormal(x: int) -> int:
    """Mock: Return ``True`` if *x* is a normal number, that is a finite nonzero number that is not a subnormal (see :func:`issubnorm..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def issubnormal(x: int) -> int:
    """Mock: Return ``True`` if *x* is a subnormal number, that is a finite nonzero number with a magnitude smaller than :data:`sys.f..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isinf(x: int) -> int:
    """Mock: Return ``True`` if *x* is a positive or negative infinity, and ``False`` otherwise."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isnan(x: int) -> int:
    """Mock: Return ``True`` if *x* is a NaN (not a number), and ``False`` otherwise."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ldexp(x: int, i: int) -> int:
    """Mock: Return ``x * (2**i)``.  This is essentially the inverse of function :func:`frexp`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nextafter(x: int, y: int, steps: int) -> int:
    """Mock: Return the floating-point value *steps* steps after *x* towards *y*. If *x* is equal to *y*, return *y*, unless *steps* ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def signbit(x: int) -> int:
    """Mock: Return ``True`` if the sign of *x* is negative and ``False`` otherwise. This is useful to detect the sign bit of zeroes,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ulp(x: int) -> int:
    """Mock: Return the value of the least significant bit of the float *x*: * If *x* is a NaN (not a number), return *x*. * If *x* i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cbrt(x: int) -> int:
    """Mock: Return the cube root of *x*. .. versionadded:: 3.11"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exp(x: int) -> int:
    """Mock: Return *e* raised to the power *x*, where *e* = 2.718281... is the base of natural logarithms.  This is usually more acc..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exp2(x: int) -> int:
    """Mock: Return *2* raised to the power *x*. .. versionadded:: 3.11"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def expm1(x: int) -> int:
    """Mock: Return *e* raised to the power *x*, minus 1.  Here *e* is the base of natural logarithms.  For small floats *x*, the sub..."""
    return 0

#@ \trusted
#@ requires x >= 0
#@ ensures \result >= 0
def log(x: int, base: int) -> int:
    """Mock: With one argument, return the natural logarithm of *x* (to base *e*). With two arguments, return the logarithm of *x* to..."""
    return 0

#@ \trusted
#@ requires x >= 0
#@ ensures \result >= 0
def log1p(x: int) -> int:
    """Mock: Return the natural logarithm of *1+x* (base *e*). The result is calculated in a way which is accurate for *x* near zero."""
    return 0

#@ \trusted
#@ requires x >= 0
#@ ensures \result >= 0
def log2(x: int) -> int:
    """Mock: Return the base-2 logarithm of *x*. This is usually more accurate than ``log(x, 2)``. .. versionadded:: 3.3 .. seealso::..."""
    return 0

#@ \trusted
#@ requires x >= 0
#@ ensures \result >= 0
def log10(x: int) -> int:
    """Mock: Return the base-10 logarithm of *x*.  This is usually more accurate than ``log(x, 10)``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pow(x: int, y: int) -> int:
    """Mock: Return *x* raised to the power *y*.  Exceptional cases follow the IEEE 754 standard as far as possible.  In particular, ..."""
    return 0

#@ \trusted
#@ requires x >= 0
#@ ensures \result >= 0
def sqrt(x: int) -> int:
    """Mock: Return the square root of *x*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dist(p: int, q: int) -> int:
    """Mock: Return the Euclidean distance between two points *p* and *q*, each given as a sequence (or iterable) of coordinates.  Th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fsum(iterable: int) -> int:
    """Mock: Return an accurate floating-point sum of values in the iterable.  Avoids loss of precision by tracking multiple intermed..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def hypot() -> int:
    """Mock: Return the Euclidean norm, ``sqrt(sum(x**2 for x in coordinates))``. This is the length of the vector from the origin to..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def prod(iterable: int, start: int) -> int:
    """Mock: Calculate the product of all the elements in the input *iterable*. The default *start* value for the product is ``1``. W..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sumprod(p: int, q: int) -> int:
    """Mock: Return the sum of products of values from two iterables *p* and *q*. Raises :exc:`ValueError` if the inputs do not have ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def degrees(x: int) -> int:
    """Mock: Convert angle *x* from radians to degrees."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def radians(x: int) -> int:
    """Mock: Convert angle *x* from degrees to radians."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def acos(x: int) -> int:
    """Mock: Return the arc cosine of *x*, in radians. The result is between ``0`` and ``pi``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def asin(x: int) -> int:
    """Mock: Return the arc sine of *x*, in radians. The result is between ``-pi/2`` and ``pi/2``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def atan(x: int) -> int:
    """Mock: Return the arc tangent of *x*, in radians. The result is between ``-pi/2`` and ``pi/2``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def atan2(y: int, x: int) -> int:
    """Mock: Return ``atan(y / x)``, in radians. The result is between ``-pi`` and ``pi``. The vector in the plane from the origin to..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cos(x: int) -> int:
    """Mock: Return the cosine of *x* radians."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sin(x: int) -> int:
    """Mock: Return the sine of *x* radians."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tan(x: int) -> int:
    """Mock: Return the tangent of *x* radians."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def acosh(x: int) -> int:
    """Mock: Return the inverse hyperbolic cosine of *x*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def asinh(x: int) -> int:
    """Mock: Return the inverse hyperbolic sine of *x*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def atanh(x: int) -> int:
    """Mock: Return the inverse hyperbolic tangent of *x*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cosh(x: int) -> int:
    """Mock: Return the hyperbolic cosine of *x*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sinh(x: int) -> int:
    """Mock: Return the hyperbolic sine of *x*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tanh(x: int) -> int:
    """Mock: Return the hyperbolic tangent of *x*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def erf(x: int) -> int:
    """Mock: Return the `error function <https://en.wikipedia.org/wiki/Error_function>`_ at *x*. The :func:`erf` function can be used..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def erfc(x: int) -> int:
    """Mock: Return the complementary error function at *x*.  The `complementary error function <https://en.wikipedia.org/wiki/Error_..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gamma(x: int) -> int:
    """Mock: Return the `Gamma function <https://en.wikipedia.org/wiki/Gamma_function>`_ at *x*. .. versionadded:: 3.2"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lgamma(x: int) -> int:
    """Mock: Return the natural logarithm of the absolute value of the Gamma function at *x*. .. versionadded:: 3.2"""
    return 0
