# Formal tests for pycsl_lib/cvar — contextvars module
from pycsl_lib.cvar import context_var_get, context_var_set, copy_context


#@ requires default >= 0
#@ ensures \result == default
def test_get_returns_default(default: int) -> int:
    """Get returns default when not set."""
    return context_var_get(default)


#@ requires value >= 0
#@ ensures \result == value
def test_set_returns_value(value: int) -> int:
    """Set returns the token (value)."""
    return context_var_set(value)


#@ ensures \result >= 0
def test_copy_nonneg() -> int:
    """copy_context returns non-negative."""
    return copy_context()
