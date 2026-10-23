r"""Test 1973 — gen #36 (expected FAIL): NON-VACUITY twin of 1972 — the copy has exactly
the source's length, so `\result == len(node.tail) + 1` must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Entry:
    kind: str
    line: int
    items: List[str] = field(default_factory=list)


@dataclass
class Node:
    line: int
    tail: List[str] = field(default_factory=list)


class Collector:
    #@ \trusted
    #@ requires 0 <= k
    #@ assigns \nothing
    def none(self, k: int) -> List[Entry]:
        return []

    #@ requires 0 <= node.line
    #@ ensures \result == len(node.tail) + 1
    #@ assigns \nothing
    def count(self, node: Node) -> int:
        e = Entry("trailer", node.line, list(node.tail))
        return len(e.items)
