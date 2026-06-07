# Formal test for linecache (lcache) module
#
# Based on library_reference/linecache.rst:
#   "Get line lineno from file named filename... Return '' if not found."
#   "Return a list of lines... for the named file."
#
# Tests:
#   1. getline returns non-negative
#   2. getlines returns non-negative
#   3. checkcache returns non-negative

from pure_lib.lcache import getline, getlines, checkcache


#@ ensures \result >= 0
def test_getline_nonneg() -> int:
    """getline result is non-negative (empty string = 0)."""
    return getline(1, 1)


#@ ensures \result >= 0
def test_getlines_nonneg() -> int:
    """getlines result (line count) is non-negative."""
    return getlines(10)


#@ ensures \result >= 0
def test_checkcache_nonneg() -> int:
    """checkcache invalidation count is non-negative."""
    return checkcache(5)
