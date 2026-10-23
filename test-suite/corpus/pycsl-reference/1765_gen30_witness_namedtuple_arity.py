r"""Test 1765 — WITNESS: a NamedTuple constructed with the wrong number of arguments.

N7 / PEP 526 — a NamedTuple's fields are required positional arguments, so a construction
with too few (or too many) is refused rather than padded. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import NamedTuple

_ = 0  # anchor


class Point(NamedTuple):
    x: int
    y: int


#@ ensures \result >= 0
def build() -> int:
    p = Point(1)
    return p.x
