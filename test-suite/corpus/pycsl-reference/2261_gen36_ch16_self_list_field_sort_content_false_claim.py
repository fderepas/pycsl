r"""Test 2261 — gen #36 ch16 (expected FAIL): non-vacuity twin of 2260. After
`self.xs.sort()` the first element is NOT the old first element: CPython turns `[1, 0]`
into `[0, 1]`, so `self.xs[0] == 1` is FALSE of the program and must stay unproved (the
in-place havoc keeps the length, never the contents).
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
    #@ ensures self.xs[0] == 1
    #@ assigns self.xs
    def order(self) -> None:
        self.xs.sort()


if __name__ == "__main__":
    t = Tracker([1, 0])
    t.order()
    assert t.xs[0] == 0
