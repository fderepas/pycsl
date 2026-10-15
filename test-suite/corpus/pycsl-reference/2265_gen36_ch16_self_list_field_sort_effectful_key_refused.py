r"""Test 2265 — gen #36 ch16 (expected FAIL): a sort KEY that CALLS something may run
effects the in-place havoc does not model (here the key bumps `self.calls` once per
element: CPython leaves `self.calls == 2`, so `self.calls == 0` is FALSE). The
sort arm accepts only a call-free `lambda` key; this one keeps the REFUSAL.
This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List


@dataclass
class Tracker:
    xs: List[int] = field(default_factory=list)
    calls: int = 0

    #@ assigns self.calls
    def note(self, v: int) -> int:
        self.calls = self.calls + 1
        return v

    #@ requires self.calls == 0
    #@ ensures self.calls == 0
    #@ assigns self.xs, self.calls
    def order(self) -> None:
        self.xs.sort(key=lambda v: self.note(v))


if __name__ == "__main__":
    t = Tracker([2, 1])
    t.order()
    assert t.calls == 2
