"""Route #218 CARRIER (expects SUCCESS — the false certificate).

`__enter__` declares `#@ assigns self.v` and sets `self.v = 7`. The caller reads `c.v`
either side of an explicit `c.__enter__()` and claims the difference is 0. CPython answers
-7, and the TRUE twin (`#@ ensures \\result == -7`) FAILS.

The emission says why: the dunder is not emitted as a `let`, so its `#@ assigns` never
becomes a frame, and the call site is

    val c___enter___0 (self: c) : int

with NO `writes` clause — which Why3 reads as PURE. `self.v` is therefore provably
unchanged across a call that sets it to 7.

Run: pycsl.py --memory-model hoare <this file>
"""
_ = 0  # anchor


#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns self.v
    #@ ensures self.v == 7
    def __enter__(self) -> int:
        self.v = 7
        return 0


#@ ensures \result == 0
def use() -> int:
    c = C()
    before: int = c.v
    _r: int = c.__enter__()
    after: int = c.v
    return before - after
