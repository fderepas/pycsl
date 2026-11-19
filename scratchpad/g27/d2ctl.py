r"""D2 — DEFERRAL AUDIT site 2 (Module6_WhyMLTranspiler.py:289): the deferral says condition
propagation is handled by `_wrap_call_with_callee_raises_assert`, whose substitution is a
positional `zip(param_names, args)`; the default-argument fill on the dotted-call path is
gated on a `self.` receiver, so on `c.f()` the callee's `k` is rendered in the CALLER's scope."""
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


#@ requires j >= 0
#@ assigns \nothing
#@ no_exception ValueError
def caller(j: int) -> int:
    c = H()
    return c.f()
