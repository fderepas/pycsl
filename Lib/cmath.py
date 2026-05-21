"""PyCSL mock for Python's cmath module — Mathematical functions for complex numbers."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def phase(z: int) -> int:
    """Mock: Return the phase of *z* (also known as the *argument* of *z*), as a float. ``phase(z)`` is equivalent to ``math.atan2(z...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def polar(z: int) -> int:
    """Mock: Return the representation of *z* in polar coordinates.  Returns a pair ``(r, phi)`` where *r* is the modulus of *z* and ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def rect(r: int, phi: int) -> int:
    """Mock: Return the complex number *z* with polar coordinates *r* and *phi*. Equivalent to ``complex(r * math.cos(phi), r * math...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exp(z: int) -> int:
    """Mock: Return *e* raised to the power *z*, where *e* is the base of natural logarithms."""
    return 0

#@ \trusted
#@ requires z >= 0
#@ ensures \result >= 0
def log(z: int, base: int) -> int:
    """Mock: Return the logarithm of *z* to the given *base*. If the *base* is not specified, returns the natural logarithm of *z*. T..."""
    return 0

#@ \trusted
#@ requires z >= 0
#@ ensures \result >= 0
def log10(z: int) -> int:
    """Mock: Return the base-10 logarithm of *z*. This has the same branch cut as :func:`log`."""
    return 0

#@ \trusted
#@ requires z >= 0
#@ ensures \result >= 0
def sqrt(z: int) -> int:
    """Mock: Return the square root of *z*. This has the same branch cut as :func:`log`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def acos(z: int) -> int:
    """Mock: Return the arc cosine of *z*. There are two branch cuts: One extends right from 1 along the real axis to ∞. The other ex..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def asin(z: int) -> int:
    """Mock: Return the arc sine of *z*. This has the same branch cuts as :func:`acos`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def atan(z: int) -> int:
    """Mock: Return the arc tangent of *z*. There are two branch cuts: One extends from ``1j`` along the imaginary axis to ``∞j``. Th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cos(z: int) -> int:
    """Mock: Return the cosine of *z*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sin(z: int) -> int:
    """Mock: Return the sine of *z*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tan(z: int) -> int:
    """Mock: Return the tangent of *z*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def acosh(z: int) -> int:
    """Mock: Return the inverse hyperbolic cosine of *z*. There is one branch cut, extending left from 1 along the real axis to -∞."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def asinh(z: int) -> int:
    """Mock: Return the inverse hyperbolic sine of *z*. There are two branch cuts: One extends from ``1j`` along the imaginary axis t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def atanh(z: int) -> int:
    """Mock: Return the inverse hyperbolic tangent of *z*. There are two branch cuts: One extends from ``1`` along the real axis to `..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cosh(z: int) -> int:
    """Mock: Return the hyperbolic cosine of *z*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sinh(z: int) -> int:
    """Mock: Return the hyperbolic sine of *z*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tanh(z: int) -> int:
    """Mock: Return the hyperbolic tangent of *z*."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isfinite(z: int) -> int:
    """Mock: Return ``True`` if both the real and imaginary parts of *z* are finite, and ``False`` otherwise. .. versionadded:: 3.2"""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isinf(z: int) -> int:
    """Mock: Return ``True`` if either the real or the imaginary part of *z* is an infinity, and ``False`` otherwise."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isnan(z: int) -> int:
    """Mock: Return ``True`` if either the real or the imaginary part of *z* is a NaN, and ``False`` otherwise."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isclose(a: int, b: int, rel_tol: int, abs_tol: int) -> int:
    """Mock: Return ``True`` if the values *a* and *b* are close to each other and ``False`` otherwise. Whether or not two values are..."""
    return 0
