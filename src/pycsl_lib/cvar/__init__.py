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


#@ requires default >= 0
#@ ensures \result == default
def context_var_get(default: int) -> int:
    """Get context variable value (returns default if not set)."""
    return default


#@ requires value >= 0
#@ ensures \result == value
def context_var_set(value: int) -> int:
    """Set context variable value. Returns Token (the value)."""
    return value


#@ ensures \result >= 0
def copy_context() -> int:
    """Copy current context. Returns depth 0 for new copy."""
    return 0
