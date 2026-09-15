r"""Q1 — deferral-audit: `_emit_option_tuple_unpack`'s docstring asserts "The Python guard
`if X is not None:` makes the `None` arm dead" but the emitter never checks for a guard.
CPython raises TypeError unpacking None."""
from typing import Optional, Tuple
_ = 0  # anchor


#@ ensures \result == 7
#@ assigns \nothing
def f(p: Optional[Tuple[int, int]]) -> int:
    a, b = p
    return 7
