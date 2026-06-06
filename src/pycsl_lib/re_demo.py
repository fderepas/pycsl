"""Formal driver for the re stub: thin annotated wrappers over re's
module-level helpers, each contract discharged from the callee's `ensures`.
Verified end-to-end (no `\trusted`) via `pycsl src/pycsl_lib/re_demo.py`."""
import re


#@ requires pattern >= 0 and string >= 0 and flags >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_search(pattern: int, string: int, flags: int) -> int:
    """Search pattern in string; returns a non-negative match handle."""
    return re.search(pattern, string, flags)


#@ requires pattern >= 0 and string >= 0 and flags >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_match(pattern: int, string: int, flags: int) -> int:
    """Match at start of string; returns a non-negative handle."""
    return re.re_match(pattern, string, flags)


#@ requires pattern >= 0 and flags >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_compile(pattern: int, flags: int) -> int:
    """Compile pattern; returns a non-negative handle."""
    return re.compile(pattern, flags)


#@ requires pattern >= 0 and string >= 0 and flags >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_fullmatch(pattern: int, string: int, flags: int) -> int:
    """Full match pattern against string; returns a non-negative handle."""
    return re.fullmatch(pattern, string, flags)


#@ requires pattern >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_escape(pattern: int) -> int:
    """Escape special chars; returns a non-negative result."""
    return re.escape(pattern)


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def demo_purge() -> int:
    """Clear the regex cache; returns 0."""
    return re.purge()
