# Formal test for linecache (lcache) module
#
# Based on library_reference/linecache.rst:
#   "Get line lineno from file. This function will never raise an
#    exception — it will return '' on errors."
#   "Return the set of valid signal numbers on this platform."

from pure_lib.lcache import getline, getlines, checkcache, lazycache


#@ ensures \result >= 0
def test_getline_nonneg() -> int:
    """RST: 'never raise an exception — return empty on errors.' Result >= 0."""
    return getline(1, 1)


#@ ensures \result >= 0
def test_getlines_nonneg() -> int:
    """RST: 'Return a list of lines.' Line count >= 0."""
    return getlines(10)


#@ ensures \result >= 0
def test_checkcache_nonneg() -> int:
    """RST: 'Check the cache for validity.' Invalidated count >= 0."""
    return checkcache(5)


#@ ensures \result >= 0 and \result <= 1
def test_lazycache_bool() -> int:
    """RST: 'Capture enough detail.' Returns 0 (fail) or 1 (success)."""
    return lazycache(10, 0)
