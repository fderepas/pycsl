r"""Test 2262 — gen #36 ch16 (expected FAIL): frame twin of 2260. `self.xs.sort()` WRITES
`self.xs` (CPython reorders `[2, 1]` in place), so a method declaring `#@ assigns \nothing`
lies about its frame; the in-place lowering puts `self.xs` in the effect and Why3 rejects
the unlisted write.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List


@dataclass
class Tracker:
    xs: List[int] = field(default_factory=list)

    #@ assigns \nothing
    def order(self) -> None:
        self.xs.sort()


if __name__ == "__main__":
    t = Tracker([2, 1])
    t.order()
    assert t.xs == [1, 2]
