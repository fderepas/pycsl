r"""Test 2002 — gen #36 (expected PASS): a PINNED record (`Entry`, the element of a
`List[Entry]` return, so its `List[str]` field is the pure `seq string` carrier) built from
a `seq string` LOCAL (`acc`, grown by `.extend` of a `-> List[str]` method). At base (outside
`@mutable_state`) the constructor DROPPED the actual for the `Seq.empty` default; now the
field binds `!acc` itself, so `len(e.items)` is proved to be the accumulated length. Twin:
2003 (must FAIL).
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

    #@ \trusted
    #@ ensures len(\result) == 2
    #@ assigns \nothing
    def norm(self, xs: List[str]) -> List[str]:
        return ["x", "y"]

    #@ ensures \result == 2
    #@ assigns \nothing
    def count(self, xs: List[str]) -> int:
        acc: List[str] = []
        acc.extend(self.norm(xs))
        e = Entry("block", 1, acc)
        return len(e.items)
