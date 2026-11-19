"""Test 0860 — WL-05d regression lock (NEGATIVE): a FALSE post-store claim must FAIL. # pycsl-expected: FAIL

wrong-lowering-to-fix.md §WL-05d (soundness twin of 0858). The `writes {p.x}` frame is
genuinely CHECKED: a record-param mutator that overwrites `p.x` to 5 but CLAIMS the field
is UNCHANGED (`#@ requires p.x == 3` then `#@ ensures p.x == 3`) must NOT prove. This IS
the severity-1 fail-OPEN that WL-05d fixed — before the fix the store was a silent no-op,
so this proved Valid on BOTH Alt-Ergo and Z3 (a false green: real Python has p.x == 5).
UNPROVABLE ⇒ XFAIL: the store is modelled and the frame constrains the post-state.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


#@ requires p.x == 3
#@ ensures p.x == 3
def setx(p: Point) -> None:
    p.x = 5
