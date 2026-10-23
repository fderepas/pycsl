# Formal tests for pycsl_lib/cvar — contextvars module
from pycsl_lib.cvar import context_var_get, context_var_set, copy_context


# (#49) gen #30: `context_var_get` now takes the UNSET assumption as a parameter, so this
# driver must supply it. It used to prove the default is returned UNCONDITIONALLY.
#@ requires default >= 0
#@ ensures \result == default
def test_get_returns_default_when_unset(default: int) -> int:
    """Get returns the default in the unset case, and only there."""
    return context_var_get(default, 0)


# (#49) gen #30: this driver PROVED `\result == value` for `ContextVar.set` under a
# docstring that conflated the two ("the token (value)"). CPython returns a `Token`, which
# is not the value. The claim left is that the handle is well-formed.
#@ requires value >= 0
#@ ensures \result >= 0
def test_set_returns_handle(value: int) -> int:
    """Set returns an opaque non-negative token handle, NOT the value."""
    return context_var_set(value)


#@ ensures \result >= 0
def test_copy_nonneg() -> int:
    """copy_context returns non-negative."""
    return copy_context()
