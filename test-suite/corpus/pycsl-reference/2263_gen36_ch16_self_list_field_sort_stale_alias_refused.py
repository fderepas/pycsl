r"""Test 2263 — gen #36 ch16 (expected FAIL): STALE-ALIAS attempt. `ys = self.xs` binds a
second name to the SAME list; `self.xs.sort()` reorders it in place, so CPython returns
`ys[0] == 0` from `[1, 0]` and the claim `\result == 1` is FALSE. A model in which `ys` is a
copy would prove it (spike ch16 `sort_weak.mlw` f3: Valid), so the sort arm REFUSES any
function that names the receiver field anywhere but `len(...)`; the call falls through to
the in-place-mutator refusal. This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List


@dataclass
class Tracker:
    xs: List[int] = field(default_factory=list)

    #@ requires \length(self.xs) == 2
    #@ requires self.xs[0] == 1
    #@ requires self.xs[1] == 0
    #@ ensures \result == 1
    #@ assigns self.xs
    def order(self) -> int:
        ys = self.xs
        self.xs.sort()
        return ys[0]


if __name__ == "__main__":
    assert Tracker([1, 0]).order() == 0
