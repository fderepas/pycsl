r"""Test 2012 — route #235 (expected PASS): CONTROL / non-vacuity twin of 2006. The field built
from a supplied actual is unconstrained but still a `seq string`, so the TRUE claim
`len(e.items) >= 0` PROVES (the record literal stays well-typed and usable).
"""
# pycsl-expected: PASS
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

    #@ requires len(xs) == 3
    #@ ensures \result >= 0
    #@ assigns \nothing
    def count(self, xs: List[str]) -> int:
        e = Entry("block", 1, xs)
        return len(e.items)
