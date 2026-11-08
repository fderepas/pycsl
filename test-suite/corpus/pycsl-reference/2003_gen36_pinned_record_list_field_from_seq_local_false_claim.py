r"""Test 2003 — gen #36 (expected FAIL): NON-VACUITY twin of 2002 — the field IS the
accumulated list (length 2), so `\result == 0` (the dropped-actual `Seq.empty`) must NOT prove.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List


@dataclass
class Entry:
    kind: str
    line: int
    items: List[str] = field(default_factory=list)


class Collector:
    def __init__(self) -> None:
        self.n = 0

    #@ \trusted
    #@ requires 0 <= k
    #@ assigns \nothing
    def none(self, k: int) -> List[Entry]:
        return []

    #@ \trusted
    #@ ensures len(\result) == 2
    #@ assigns \nothing
    def norm(self, xs: List[str]) -> List[str]:
        return ["x", "y"]

    #@ ensures \result == 0
    #@ assigns \nothing
    def count(self, xs: List[str]) -> int:
        acc: List[str] = []
        acc.extend(self.norm(xs))
        e = Entry("block", 1, acc)
        return len(e.items)
