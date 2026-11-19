r"""Test 2006 — route #235 (expected FAIL): a PINNED record (`Entry`, the element of a
`List[Entry]` return, so its `List[str]` field is the pure `seq string` carrier) built from a
SUPPLIED positional actual `xs` with `len(xs) == 3`. At base the constructor dropped the actual
for the DEFINITE `Seq.empty` default and `len(e.items) == 0` PROVED (CPython returns 3); the
field is now UNCONSTRAINED (`any_seq`), so the false claim must not prove. Control: 2012.
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
        e = Entry("block", 1, xs)
        return len(e.items)
