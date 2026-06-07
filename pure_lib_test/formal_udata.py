# Formal tests for pure_lib/udata — unicodedata module
from pure_lib.udata import lookup, normalize


#@ requires name >= 0
#@ ensures \result >= 0
def test_lookup_nonneg(name: int) -> int:
    """lookup returns non-negative codepoint."""
    return lookup(name)


#@ requires s >= 0
#@ ensures \result >= 0
def test_normalize_nonneg(s: int) -> int:
    """normalize returns non-negative."""
    return normalize(0, s)
