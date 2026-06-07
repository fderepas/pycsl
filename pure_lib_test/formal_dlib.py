# Formal tests for pure_lib/dlib — difflib module
from pure_lib.dlib import unified_diff_lines, context_diff_lines, get_close_matches


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def test_unified_nonneg(a: int, b: int) -> int:
    """Unified diff has non-negative lines."""
    return unified_diff_lines(a, b)


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def test_context_nonneg(a: int, b: int) -> int:
    """Context diff has non-negative lines."""
    return context_diff_lines(a, b)


#@ requires n >= 0
#@ ensures \result >= 0
def test_close_matches_bounded(n: int) -> int:
    """Close matches returns at most n."""
    return get_close_matches(0, n)
