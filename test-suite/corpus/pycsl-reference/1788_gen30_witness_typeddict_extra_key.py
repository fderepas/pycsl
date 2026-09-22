r"""Test 1788 — WITNESS: a TypedDict literal carrying a key the TypedDict does not declare.

T9 / PEP 589. A literal must not provide keys outside the declared set: an undeclared key
has no field to be lowered into, so it would simply vanish from the model while staying in
the program. One of the refusals `bin/check-refusal-witness-coverage.py` measured as having
no witness.
"""
# pycsl-expected: FAIL
from typing import TypedDict

_ = 0  # anchor


class Pt(TypedDict):
    x: int
    y: int


#@ requires True
#@ assigns \nothing
def build() -> Pt:
    return {"x": 1, "y": 2, "z": 3}
