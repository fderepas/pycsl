r"""Test 1913 — gen #32 (expected PASS): ROUTE #227's SECOND COMPLETENESS CONTROL — the
guarded idiom, which is where the real code lives.

`v` is `None` on one path and `1` on another, so `functions.py` pre-seeds the record as
`"AMBIG"` rather than `"None#empty"`, and #227's fence — which fires only on the CERTAIN
entry — cannot reach it. That matters because AMBIG is exactly where the legitimate
short-circuit and narrowing idioms live: the 4531-file census for #227 found only THREE
sites, and both of the real-code ones are this shape —
`if last_end is None or start >= last_end` over a loop-rebound local, and
`v = None  # defer bool` read under `isinstance(v, int)` in PyCSL's own emitter.

`f(1)` is 3 and `f(0)` is 3 in Python, on both paths, so the program is true and must keep
proving. A fence that took this file with it would have deleted a capability rather than a
falsehood.
"""
# pycsl-expected: PASS
_ = 0  # anchor
from typing import Optional

#@ ensures \result == 3
#@ no_exception \all
#@ assigns \nothing
def f(c: int) -> int:
    v = None  # type: Optional[int]
    if c > 0:
        v = 1
    if v is not None:
        return v - v + 3
    return 3
