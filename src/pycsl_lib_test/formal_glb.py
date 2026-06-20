# Formal tests for pycsl_lib/glb — glob
from pycsl_lib.glb import glob_count, escape, has_magic


#@ requires pat >= 0
#@ ensures \result >= 0
def test_glob_nonneg(pat: int) -> int:
    """glob returns non-negative match count."""
    return glob_count(pat)


#@ requires pathname >= 0
#@ ensures \result >= pathname
def test_escape_grows(pathname: int) -> int:
    """escape output >= input (adds backslashes)."""
    return escape(pathname)


#@ requires pat >= 0
#@ ensures \result == 1 or \result == 0
def test_has_magic_boolean(pat: int) -> int:
    """has_magic returns 0 or 1."""
    return has_magic(pat)
