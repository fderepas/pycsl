r"""Test 2011 — route #235 (expected PASS): CONTROL. The `items` actual is OMITTED, so
`default_factory=list` runs and the field IS empty; the faithful `Seq.empty` default is kept and
`len(e.items) == 0` still PROVES. Bounds the repair: only a SUPPLIED actual is unconstrained.
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

    #@ requires 0 <= k
    #@ ensures \result == 0
    #@ assigns \nothing
    def count(self, k: int) -> int:
        e = Entry("block", k)
        return len(e.items)
