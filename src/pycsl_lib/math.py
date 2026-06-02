"""PyCSL mock for Python's math module.

Provides trusted stubs for mathematical functions: floating point
arithmetic, manipulation, power/exponential/logarithmic, summation,
angular conversion, trigonometric, hyperbolic, special, and
number-theoretic functions plus constants.
"""
_ = 0  # anchor

# ── Constants ───────────────────────────────────────────────────────

pi = 0
e = 0
tau = 0
inf = 0
nan = 0

# ── Floating point arithmetic ──────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/math.html#math.ceil
#@ requires True
#@ ensures \result >= x
#@ ensures \result <= x + 1
def ceil(x: int) -> int:
    """Mock: return the ceiling of x, the smallest integer >= x.

    For the int-domain mock, ceil is the identity: ceil(n) == n
    for any integer n. The contract `x <= \\result <= x + 1`
    holds in the real float-domain version (where the +1 fires
    on any non-integral input). The weaker bound is sound for
    both interpretations and avoids over-committing the mock.
    """
    return 0

#@ \trusted
#@ ensures \result >= 0
def fabs(x: int) -> int:
    """Mock: return the absolute value of x."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/math.html#math.floor
#@ requires True
#@ ensures \result <= x
#@ ensures \result >= x - 1
def floor(x: int) -> int:
    """Mock: return the floor of x, the largest integer <= x.

    Symmetric to ceil: the int-domain mock is the identity, the
    real float-domain version drops the fractional part. The
    contract `x - 1 <= \\result <= x` is sound for both.
    """
    return 0

#@ \trusted
def fma(x: int, y: int, z: int) -> int:
    """Mock: return fused multiply-add (x * y) + z."""
    return 0

#@ \trusted
def fmax(x: int, y: int) -> int:
    """Mock: return the larger of two floating-point values."""
    return 0

#@ \trusted
def fmin(x: int, y: int) -> int:
    """Mock: return the smaller of two floating-point values."""
    return 0

#@ \trusted
def fmod(x: int, y: int) -> int:
    """Mock: return the remainder of x / y."""
    return 0

#@ \trusted
def modf(x: int) -> int:
    """Mock: return the fractional and integer parts of x."""
    return 0

#@ \trusted
def remainder(x: int, y: int) -> int:
    """Mock: return the IEEE 754-style remainder of x with respect to y."""
    return 0

#@ \trusted
def trunc(x: int) -> int:
    """Mock: return x with the fractional part removed."""
    return 0

# ── Floating point manipulation functions ──────────────────────────

#@ \trusted
def copysign(x: int, y: int) -> int:
    """Mock: return a float with magnitude of x and sign of y."""
    return 0

#@ \trusted
def frexp(x: int) -> int:
    """Mock: return the mantissa and exponent of x as a pair (m, e)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def isclose(a: int, b: int, rel_tol: int, abs_tol: int) -> int:
    """Mock: return whether values a and b are close to each other."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def isfinite(x: int) -> int:
    """Mock: return whether x is neither an infinity nor a NaN."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def isnormal(x: int) -> int:
    """Mock: return whether x is a normal number."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def issubnormal(x: int) -> int:
    """Mock: return whether x is a subnormal number."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def isinf(x: int) -> int:
    """Mock: return whether x is a positive or negative infinity."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def isnan(x: int) -> int:
    """Mock: return whether x is a NaN (not a number)."""
    return 0

#@ \trusted
def ldexp(x: int, i: int) -> int:
    """Mock: return x * (2**i)."""
    return 0

#@ \trusted
def nextafter(x: int, y: int, steps: int) -> int:
    """Mock: return the float value steps steps after x towards y."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def signbit(x: int) -> int:
    """Mock: return whether the sign of x is negative."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ulp(x: int) -> int:
    """Mock: return the value of the least significant bit of x."""
    return 0

# ── Power, exponential and logarithmic functions ───────────────────

#@ \trusted
def cbrt(x: int) -> int:
    """Mock: return the cube root of x."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exp(x: int) -> int:
    """Mock: return e raised to the power x."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exp2(x: int) -> int:
    """Mock: return 2 raised to the power x."""
    return 0

#@ \trusted
def expm1(x: int) -> int:
    """Mock: return e raised to the power x, minus 1."""
    return 0

#@ \trusted
def log(x: int, base: int) -> int:
    """Mock: return the logarithm of x to the given base."""
    return 0

#@ \trusted
def log1p(x: int) -> int:
    """Mock: return the natural logarithm of 1+x."""
    return 0

#@ \trusted
def log2(x: int) -> int:
    """Mock: return the base-2 logarithm of x."""
    return 0

#@ \trusted
def log10(x: int) -> int:
    """Mock: return the base-10 logarithm of x."""
    return 0

#@ \trusted
def pow(x: int, y: int) -> int:
    """Mock: return x raised to the power y."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/math.html#math.sqrt
#@ requires x >= 0
#@ ensures \result >= 0
#@ ensures \result * \result <= x
#@ ensures (\result + 1) * (\result + 1) > x
def sqrt(x: int) -> int:
    """Mock: return the square root of x.

    Real Python's math.sqrt raises ValueError when x < 0. This
    stub models the non-negative branch only — callers that
    can't establish x >= 0 fail to verify, which is the
    desired behavior. The two `ensures` clauses pin the
    result to the integer square root: r² ≤ x < (r+1)².
    """
    return 0

# ── Summation and product functions ────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def dist(p: int, q: int) -> int:
    """Mock: return the Euclidean distance between two points p and q."""
    return 0

#@ \trusted
def fsum(iterable: int) -> int:
    """Mock: return an accurate floating-point sum of values in the iterable."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def hypot(x: int, y: int) -> int:
    """Mock: Euclidean norm. `math.hypot` is variadic; this stub models the
    common two-argument case so demos can call `hypot(x, y)` (a unary signature
    caused `int -> int applied to 2 arguments`)."""
    return 0

#@ \trusted
def prod(iterable: int, start: int) -> int:
    """Mock: return the product of all elements in the input iterable."""
    return 0

#@ \trusted
def sumprod(p: int, q: int) -> int:
    """Mock: return the sum of products from two iterables p and q."""
    return 0

# ── Angular conversion ─────────────────────────────────────────────

#@ \trusted
def degrees(x: int) -> int:
    """Mock: convert angle x from radians to degrees."""
    return 0

#@ \trusted
def radians(x: int) -> int:
    """Mock: convert angle x from degrees to radians."""
    return 0

# ── Trigonometric functions ────────────────────────────────────────

#@ \trusted
def acos(x: int) -> int:
    """Mock: return the arc cosine of x, in radians."""
    return 0

#@ \trusted
def asin(x: int) -> int:
    """Mock: return the arc sine of x, in radians."""
    return 0

#@ \trusted
def atan(x: int) -> int:
    """Mock: return the arc tangent of x, in radians."""
    return 0

#@ \trusted
def atan2(y: int, x: int) -> int:
    """Mock: return atan(y / x), in radians."""
    return 0

#@ \trusted
def cos(x: int) -> int:
    """Mock: return the cosine of x radians."""
    return 0

#@ \trusted
def sin(x: int) -> int:
    """Mock: return the sine of x radians."""
    return 0

#@ \trusted
def tan(x: int) -> int:
    """Mock: return the tangent of x radians."""
    return 0

# ── Hyperbolic functions ───────────────────────────────────────────

#@ \trusted
def acosh(x: int) -> int:
    """Mock: return the inverse hyperbolic cosine of x."""
    return 0

#@ \trusted
def asinh(x: int) -> int:
    """Mock: return the inverse hyperbolic sine of x."""
    return 0

#@ \trusted
def atanh(x: int) -> int:
    """Mock: return the inverse hyperbolic tangent of x."""
    return 0

#@ \trusted
def cosh(x: int) -> int:
    """Mock: return the hyperbolic cosine of x."""
    return 0

#@ \trusted
def sinh(x: int) -> int:
    """Mock: return the hyperbolic sine of x."""
    return 0

#@ \trusted
def tanh(x: int) -> int:
    """Mock: return the hyperbolic tangent of x."""
    return 0

# ── Special functions ──────────────────────────────────────────────

#@ \trusted
def erf(x: int) -> int:
    """Mock: return the error function at x."""
    return 0

#@ \trusted
def erfc(x: int) -> int:
    """Mock: return the complementary error function at x."""
    return 0

#@ \trusted
def gamma(x: int) -> int:
    """Mock: return the Gamma function at x."""
    return 0

#@ \trusted
def lgamma(x: int) -> int:
    """Mock: return the natural log of the absolute value of Gamma at x."""
    return 0

# ── Number-theoretic functions ─────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def comb(n: int, k: int) -> int:
    """Mock: return the number of ways to choose k items from n without order."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def factorial(n: int) -> int:
    """Mock: return n factorial."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/math.html#math.gcd
#@ requires a >= 0 and b >= 0
#@ ensures \result >= 0
def gcd(a: int, b: int) -> int:
    """Mock: greatest common divisor. `math.gcd` is variadic; this stub models
    the common two-argument case so demos can call `gcd(a, b)` (a unary
    signature caused `int -> int applied to 2 arguments`). gcd is non-negative.
    """
    return 0

#@ \trusted
#@ ensures \result >= 0
def isqrt(n: int) -> int:
    """Mock: return the integer square root of nonneg integer n."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lcm(a: int, b: int) -> int:
    """Mock: least common multiple. `math.lcm` is variadic; this stub models the
    common two-argument case so demos can call `lcm(a, b)` (a unary signature
    caused `int -> int applied to 2 arguments`)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def perm(n: int, k: int) -> int:
    """Mock: return the number of ways to choose k items from n with order."""
    return 0
