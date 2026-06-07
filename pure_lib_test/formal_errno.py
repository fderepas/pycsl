# Formal tests for pure_lib/errno
from pure_lib.errno import strerror, errorcode_count


#@ requires code >= 0
#@ ensures \result >= 0
def test_strerror_nonneg(code: int) -> int:
    """strerror returns non-negative string length."""
    return strerror(code)


#@ ensures \result > 0
def test_errorcode_positive() -> int:
    """At least one error code exists."""
    return errorcode_count()
