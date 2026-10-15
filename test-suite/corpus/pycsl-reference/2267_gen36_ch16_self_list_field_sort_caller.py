r"""Test 2267 — gen #36 ch16 (expected PASS): a CALLER of the in-place sort sees the
declared frame. `order` sorts `self.xs` under `#@ assigns self.xs`; the caller's call
avatar is `val self_order_0 (self: tracker) : unit writes { self.xs }`, so `self.n` is
provably untouched across the call (CPython: `n` stays 7). (The avatar carries the frame
but not the callee's length `ensures`, so a caller-side LENGTH claim does not prove today —
a completeness gap of method avatars, unrelated to the sort lowering.) Control for 2260.
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import List


@dataclass
class Tracker:
    xs: List[int] = field(default_factory=list)
    n: int = 0

    #@ ensures \length(self.xs) == \old(\length(self.xs))
    #@ assigns self.xs
    def order(self) -> None:
        self.xs.sort()

    #@ ensures self.n == \old(self.n)
    #@ assigns self.xs
    def run(self) -> None:
        self.order()


if __name__ == "__main__":
    t = Tracker([3, 1, 2], 7)
    t.run()
    assert t.n == 7 and t.xs == [1, 2, 3]
