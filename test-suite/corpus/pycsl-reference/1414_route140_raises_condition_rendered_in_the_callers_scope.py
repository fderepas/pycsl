r"""Test 1414 — ROUTE #140: `_wrap_call_with_callee_raises_assert` substitutes actuals positionally with `zip(param_names, args)`, and the default-argument fill on the dotted-call path is gated on a `self.` receiver. On `c.f()` with `f(self, k: int = -1)` and `raises ValueError when k < 0`, `args` is empty and the callee\x27s `k` renders in the CALLER\x27s scope, so `assert { not (k < 0) }` is discharged from the caller\x27s own `k`. The contract PROVED while CPython raises ValueError.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class H:
    tag: int

    def __init__(self) -> None:
        self.tag = 0

    #@ raises ValueError when k < 0
    #@ assigns \nothing
    def f(self, k: int = -1) -> int:
        m = k
        if m < 0:
            raise ValueError
        return m


#@ requires k >= 0
#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    c = H()
    return c.f()