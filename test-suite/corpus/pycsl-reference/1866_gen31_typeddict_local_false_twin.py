r"""Test 1866 — gen #31 FALSE TWIN of 1865 (expected FAIL): the record really is read.

Byte-identical to 1865 except that it claims `\result == 4` where `p["x"] + p["y"]` is 3.
It FAILS, which is what separates "the local is now lowered as a record" from "the local
is now lowered as something that satisfies anything": an empty or opaque model would let
both halves through, and route #47's whole family exists because a decidable wrong answer
is worse than an undecidable one.
"""
# pycsl-expected: FAIL
from typing import TypedDict

_ = 0  # anchor


class Pt(TypedDict):
    x: int
    y: int


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    p: Pt = {"x": 1, "y": 2}
    return p["x"] + p["y"]
