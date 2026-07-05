"""Test 0859 — WL-05d regression lock (POSITIVE): record-PARAM mutation ESCAPES to caller.

wrong-lowering-to-fix.md §WL-05d (caller-visibility). Python objects are passed BY
REFERENCE, so a store to a record param field is visible to the caller. `setx` sets
`p.x = 5` (`#@ ensures p.x == 5`); `caller` calls `setx(p)` and observes the write via the
callee's postcondition. The Why3-inferred `writes {p.x}` propagates through the call —
PROVEN confirms the escape is well-typed and sound (parallel to the WL-05b dict-param 0832).
"""
_ = 0  # anchor
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


#@ ensures p.x == 5
def setx(p: Point) -> None:
    p.x = 5


#@ ensures p.x == 5
def caller(p: Point) -> None:
    setx(p)
