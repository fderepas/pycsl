# Formal tests for pycsl_lib/shlx — shlex module
from pycsl_lib.shlx import split, quote


#@ requires length >= 0
#@ ensures \result >= 0
def test_split_nonneg(length: int) -> int:
    """split returns non-negative."""
    return split(length)


def test_quote_str() -> str:
    """quote returns a string."""
    return quote("hello")
