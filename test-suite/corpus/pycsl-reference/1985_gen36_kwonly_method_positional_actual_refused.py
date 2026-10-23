r"""Test 1985 — gen #36 (expected FAIL): ROUTE #232 — a positional actual to a keyword-only METHOD formal

`C().m(3)` against `def m(self, *, k)`: CPython raises TypeError. With `k` now an emitted
parameter the method-call lowering would bind it POSITIONALLY; the call is refused fail-closed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x: int = 0

    #@ ensures \result == k
    #@ assigns \nothing
    def m(self, *, k: int) -> int:
        return k


#@ ensures \result == 3
#@ no_exception \all
#@ assigns \nothing
def g() -> int:
    c = C()
    return c.m(3)
