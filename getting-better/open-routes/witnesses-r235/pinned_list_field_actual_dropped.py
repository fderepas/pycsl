from __future__ import annotations
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
        e = Entry("block", 1, xs)
        return len(e.items)

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def count2(self) -> int:
        acc: List[str] = ["a", "b"]
        e = Entry("block", 1, acc)
        return len(e.items)
