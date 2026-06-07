# Formal test for linecache (lcache) module — universally quantified
#
# Based on library_reference/linecache.rst:
#   "Get line lineno from file. This function will never raise an
#    exception — it will return '' on errors."

from pure_lib.lcache import getline, getlines, checkcache, lazycache


#@ requires lineno >= 1 and lineno < 2147483647
#@ requires filename >= 0 and filename < 2147483647
#@ ensures \result >= 0
def test_getline_nonneg(filename: int, lineno: int) -> int:
    """getline(filename, lineno) >= 0 for all valid inputs. Never raises."""
    return getline(filename, lineno)


#@ requires filename >= 0 and filename < 2147483647
#@ ensures \result >= 0
def test_getlines_nonneg(filename: int) -> int:
    """getlines(filename) >= 0 for all filenames. Line count >= 0."""
    return getlines(filename)


#@ requires filename >= 0 and filename < 2147483647
#@ ensures \result >= 0
def test_checkcache_nonneg(filename: int) -> int:
    """checkcache(filename) >= 0 for all filenames. Invalidated count >= 0."""
    return checkcache(filename)


#@ requires filename >= 0 and filename < 2147483647
#@ requires module_globals >= 0 and module_globals < 2147483647
#@ ensures \result >= 0 and \result <= 1
def test_lazycache_bool(filename: int, module_globals: int) -> int:
    """lazycache(filename, module_globals) in {0, 1} for all inputs."""
    return lazycache(filename, module_globals)
