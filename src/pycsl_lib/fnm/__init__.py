# pycsl_lib/fnm — pure-Python fnmatch module model
# Named 'fnm' to avoid stdlib name clash.
#
# Contracts derived from library_reference/fnmatch.rst.
# RST: "This module provides support for Unix shell-style wildcards."
# RST: "fnmatch(), fnmatchcase(), filter(), translate()"
#
# Model: pattern matching as length comparison (wildcard can match anything).


#@ requires name >= 0
#@ requires pat >= 0
#@ ensures \result == 1 or \result == 0
#@ assigns \nothing
def fnmatch(name: int, pat: int) -> int:
    """RST: 'Test whether the filename string matches the pattern string.'
    Returns 1 (match) or 0 (no match)."""
    if pat == 0:
        if name == 0:
            return 1
        return 0
    return 1


#@ requires name >= 0
#@ requires pat >= 0
#@ ensures \result == 1 or \result == 0
#@ assigns \nothing
def fnmatchcase(name: int, pat: int) -> int:
    """RST: 'Test whether filename matches pattern, case-sensitive.'"""
    if pat == 0:
        if name == 0:
            return 1
        return 0
    return 1


#@ requires \length(names) >= 0
#@ requires pat >= 0
#@ ensures \result >= 0
#@ ensures \result <= \length(names)
#@ assigns \nothing
def filter_count(names: list, pat: int) -> int:
    """RST: 'Construct a list from those elements of the iterable names
    that match pattern.' Result count <= input count."""
    return len(names)


#@ requires pat >= 0
#@ ensures \result >= pat
#@ assigns \nothing
def translate(pat: int) -> int:
    """RST: 'Translate a shell PATTERN to a regular expression.'
    Regex is at least as long as pattern (adds anchors/escapes)."""
    return pat
