r"""Test 2008 — route #235 (expected FAIL): KEYWORD twin of 2006 —
`Entry(kind="block", line=1, items=xs)`. A keyword-supplied actual is as supplied as a
positional one; at base `len(e.items) == 0` PROVED (CPython returns 3).
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

    #@ requires len(xs) == 3
    #@ ensures \result == 0
    #@ assigns \nothing
    def count(self, xs: List[str]) -> int:
        e = Entry(kind="block", line=1, items=xs)
        return len(e.items)
