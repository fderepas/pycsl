r"""Test 1354 — ROUTE #121 (carrier of the first repair draft): `from functools import cached_property as memo_prop` and `@memo_prop` — the memoization gate (`_is_memoized`, route #94) keys on the SPELLING `cached_property`, so the aliased decorator was not a memoizer to it and the stale-cache contract `\result == self.a` PROVED (the unaliased twin, 1257, is refused). A canonical decorator must now be bound under its own name.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from functools import cached_property as memo_prop

#@ class invariant self.a >= 0
class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures \result == self.a
    #@ assigns \nothing
    @memo_prop
    def total(self) -> int:
        return self.a

    #@ assigns self.a
    #@ ensures self.a == \old(self.a) + 1
    def bump(self) -> None:
        self.a = self.a + 1
