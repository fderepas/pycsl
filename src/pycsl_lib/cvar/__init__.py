# Pure model for contextvars — context variables
# Models context as a stack-depth tracker.

""" # pycsl"""


#@ class invariant self._depth >= 0
class Context:
    """Abstract execution context (stack of variable bindings)."""

    #@ ensures self._depth == 0
    def __init__(self) -> None:
        self._depth: int = 0

    #@ ensures self._depth == \old(self._depth) + 1
    #@ assigns self._depth
    def run(self, func: int) -> None:
        """Run function in this context (push frame)."""
        self._depth = self._depth + 1

    #@ ensures \result == self._depth
    def copy_depth(self) -> int:
        """Return depth of context copy."""
        return self._depth


# (#49) gen #30: the clause USED TO BE unconditional, and the docstring below already
# said it should not be. MEASURED: after `cv.set(5)`, `cv.get(0)` is 5, not 0. The
# `is_set` parameter with `requires is_set == 0` puts the UNSET ASSUMPTION IN THE
# CONTRACT, where a caller who is proving things will actually see it — the previous
# spelling left it in prose, and prose is not a clause.
#@ requires default >= 0
#@ requires is_set == 0
#@ ensures \result == default
def context_var_get(default: int, is_set: int) -> int:
    """Get context variable value. `requires is_set == 0` is the UNSET case, which is
    the only one in which CPython returns the default; when the variable IS set,
    `ContextVar.get(default)` returns the stored value."""
    return default


# (#49) gen #30: the clause USED TO BE `ensures \result == value`, and the docstring
# used to say "Returns Token (the value)" — conflating the two in its own parenthesis.
# MEASURED: `ContextVar.set(5)` returns a `contextvars.Token`, the object `reset`
# consumes; it is not the value and does not compare equal to it. The model returns an
# OPAQUE NON-NEGATIVE HANDLE, which is all a Token is here, so the only claim left is
# that the handle is well-formed.
#@ requires value >= 0
#@ ensures \result >= 0
def context_var_set(value: int) -> int:
    """Set the context variable. Returns an opaque non-negative TOKEN HANDLE — real
    `ContextVar.set` returns a `Token`, which is NOT the value."""
    return value


#@ ensures \result >= 0
def copy_context() -> int:
    """Copy current context. Returns depth 0 for new copy."""
    return 0
