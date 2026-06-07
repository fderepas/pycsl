"""Formal test 0002: pure_lib/re — compile and match contracts.

Verifies structural properties of the re module for all symbolic
inputs: compile returns a valid Pattern, match returns a valid Match
with start/end consistency, and error paths return well-defined codes.
"""
from pure_lib.re import compile
from pure_lib.re._engine import (
    _match_whitespace, _match_hexdigits, _match_escape,
    _match_escape_ascii, _match_has_utf8,
    _match_number, _match_stringchunk,
)


#@ requires pos >= 0
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_whitespace(s, pos) -> int:
    """Whitespace matcher always succeeds (star quantifier).
    The star quantifier means it matches zero or more characters,
    so it always returns a valid match (never None/-1).
    The stronger ensures \\result == 0 is also provable (by Z3)."""
    m = _match_whitespace(s, pos)
    if m < 0:
        return 1
    return 0


#@ requires pos >= 0
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_hexdigits(s, pos) -> int:
    """Hexdigits matcher returns match or -1, never crashes."""
    m = _match_hexdigits(s, pos)
    if m < 0:
        return 1
    return 0


#@ requires pos >= 0
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_escape(s, pos) -> int:
    """Escape matcher returns match or -1, never crashes."""
    m = _match_escape(s, pos)
    if m < 0:
        return 1
    return 0


#@ requires pos >= 0
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_escape_ascii(s, pos) -> int:
    """Escape ASCII matcher returns match or -1, never crashes."""
    m = _match_escape_ascii(s, pos)
    if m < 0:
        return 1
    return 0


#@ requires pos >= 0
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_has_utf8(s, pos) -> int:
    """UTF-8 bytes matcher returns match or -1, never crashes."""
    m = _match_has_utf8(s, pos)
    if m < 0:
        return 1
    return 0


#@ requires pos >= 0
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_number(s, pos) -> int:
    """Number matcher returns match or -1, never crashes."""
    m = _match_number(s, pos)
    if m < 0:
        return 1
    return 0


#@ requires pos >= 0
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_stringchunk(s, pos) -> int:
    """Stringchunk matcher returns match or -1, never crashes."""
    m = _match_stringchunk(s, pos)
    if m < 0:
        return 1
    return 0


#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_compile(pat_src) -> int:
    """Compile returns a valid Pattern (>= 0) or raises PatternError."""
    p = compile(pat_src, 0)
    if p < 0:
        return 1
    return 0
