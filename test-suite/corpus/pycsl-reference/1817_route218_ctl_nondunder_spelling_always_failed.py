r"""Test 1817 — ROUTE #218 CONTROL (expected FAIL): the NON-dunder spelling, which pins
the defect to the SKIP rather than to the contract.

This is 1815 with `__enter__` renamed to `enter` and the annotations removed. A
non-dunder method is emitted as an ordinary `let`, so its write to `self.v` is in the
model and the caller cannot prove `before - after == 0`. It FAILED before route #218's
repair and it FAILS after.

That is the separating measurement: the hole was never about `#@ assigns`, about class
invariants, or about the receiver spelling. It was about `_should_skip_method` dropping
the body, and only the dunder spelling reaches that branch.
"""
# pycsl-expected: FAIL


#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    def enter(self) -> int:
        self.v = 7
        return 0


#@ ensures \result == 0
def use() -> int:
    c = C()
    before: int = c.v
    _r: int = c.enter()
    after: int = c.v
    return before - after
