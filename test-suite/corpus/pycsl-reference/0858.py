"""Test 0858 — WL-05d regression lock (POSITIVE): RECORD/@dataclass PARAMETER field store.

wrong-lowering-to-fix.md §WL-05d (record/list param field-mutation). A standalone
(non-list-element) @dataclass param is a MUTABLE Why3 record `{ mutable x; mutable y }`;
a field store `p.x = v` lowers to the NATIVE `p.x <- v` and Why3 INFERS the `writes {p.x}`
frame on the concrete `let`, so the write-read-back `#@ ensures p.x == 5` PROVES. Before
WL-05d Module 5 emitted NO IR for a non-`self` attribute-target assign, so the store was a
silent no-op (fail-OPEN). PROVEN here confirms the store is modelled and non-vacuous.
"""
_ = 0  # anchor
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


#@ ensures p.x == 5
#@ ensures p.y == 4
def setx(p: Point) -> None:
    p.y = 4
    p.x = 5
