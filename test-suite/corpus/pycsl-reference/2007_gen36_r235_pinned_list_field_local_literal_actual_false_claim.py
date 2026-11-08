r"""Test 2007 — route #235 (expected FAIL): the same PINNED record built from a LOCAL list
literal `acc = ["a", "b"]` (an `array string` let, which no faithful seq binder captures). At
base `len(e.items) == 0` PROVED (CPython returns 2); the field is now `any_seq`.
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

    #@ requires 0 <= k
    #@ ensures \result == 0
    #@ assigns \nothing
    def count2(self, k: int) -> int:
        acc: List[str] = ["a", "b"]
        e = Entry("block", 1, acc)
        return len(e.items)
