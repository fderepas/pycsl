r"""Test 2165 — ch13 seam S-a (expected PASS, faithfulness control): an `int`-element
`List[int] = field(default_factory=list)` field next to a `List[str]` one. The int field keeps its
existing `(Array.make 0 0)` default (byte-identical lowering); the str field takes the new
`(Array.make 0 "")`. CPython: both are empty (falsy), so `sizes_plus(k)` returns `k`. Control for 2163/2164.
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import List


@dataclass
class R:
    ns: List[int] = field(default_factory=list)
    xs: List[str] = field(default_factory=list)


#@ ensures \result == k
#@ assigns \nothing
def sizes_plus(k: int) -> int:
    r = R()
    if r.ns:
        return k + 1
    if r.xs:
        return k + 2
    return k
