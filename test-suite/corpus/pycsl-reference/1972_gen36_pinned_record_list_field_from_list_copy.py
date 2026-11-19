r"""Test 1972 — gen #36 (expected PASS): a PINNED record (`Entry`, the element of a
`List[Entry]` return, so its `List[str]` field is the pure `seq string` carrier) built from
`list(node.tail)`, a copy of a STRING-element list field of another record. Three links, each
an L3-tc error or a dropped operand at base: `list(<string-array field>)` fell to the opaque
`list_new : int -> int`; the record constructor then DROPPED that actual for the `Seq.empty`
default; and `len(e.items)` on the pinned seq field was the opaque `iter_length`. Now
`list(..)` is `Array.copy`, the field binds `snapshot_str (Array.copy node.tail)` (length-
and element-preserving) and `len` is `Seq.length`, so the copy's length is proved equal to
the source's. Twin: 1973 (must FAIL).
"""
# pycsl-expected: PASS
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
    #@ ensures \result == len(node.tail)
    #@ assigns \nothing
    def count(self, node: Node) -> int:
        e = Entry("trailer", node.line, list(node.tail))
        return len(e.items)
