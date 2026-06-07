# Formal tests for pure_lib/fnm — fnmatch
from pure_lib.fnm import fnmatch, fnmatchcase, filter_count, translate


#@ requires name >= 0
#@ requires pat >= 0
#@ ensures \result == 1 or \result == 0
def test_fnmatch_boolean(name: int, pat: int) -> int:
    """fnmatch returns 0 or 1."""
    return fnmatch(name, pat)


#@ requires name >= 0
#@ requires pat >= 0
#@ ensures \result == 1 or \result == 0
def test_fnmatchcase_boolean(name: int, pat: int) -> int:
    """fnmatchcase returns 0 or 1."""
    return fnmatchcase(name, pat)


#@ requires \length(names) >= 0
#@ requires pat >= 0
#@ ensures \result >= 0
#@ ensures \result <= \length(names)
def test_filter_bounded(names: list, pat: int) -> int:
    """filter result <= input length."""
    return filter_count(names, pat)


#@ requires pat >= 0
#@ ensures \result >= pat
def test_translate_grows(pat: int) -> int:
    """translate output >= input."""
    return translate(pat)
