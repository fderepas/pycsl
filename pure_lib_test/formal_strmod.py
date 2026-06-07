# Formal tests for pure_lib/strmod — string module model
from pure_lib.strmod import capwords, template_substitute, template_safe_substitute, format_field


#@ requires s >= 0
#@ ensures \result <= s
def test_capwords_bounded(s: int) -> int:
    """capwords never grows the string (removes extra whitespace)."""
    return capwords(s)


#@ ensures \result == 0
def test_capwords_empty() -> int:
    """capwords of empty is empty."""
    return capwords(0)


#@ requires t >= 0
#@ requires m >= 0
#@ ensures \result == t + m
def test_substitute_additive(t: int, m: int) -> int:
    """template_substitute produces template + mapping length."""
    return template_substitute(t, m)


#@ requires t >= 0
#@ requires m >= 0
#@ ensures \result >= t
def test_safe_substitute_monotone(t: int, m: int) -> int:
    """safe_substitute result >= template (unresolved vars stay)."""
    return template_safe_substitute(t, m)


#@ requires val >= 0
#@ ensures \result == val
def test_format_field_identity(val: int) -> int:
    """format_field with empty format is identity."""
    return format_field(0, val)
