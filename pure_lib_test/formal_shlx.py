# Formal tests for pure_lib/shlx — shlex module
from pure_lib.shlx import split, quote


#@ requires length >= 0
#@ ensures \result >= 0
def test_split_nonneg(length: int) -> int:
    """split returns non-negative."""
    return split(length)


#@ requires length >= 0
#@ ensures \result >= 0
def test_quote_nonneg(length: int) -> int:
    """quote returns non-negative."""
    return quote(length)
