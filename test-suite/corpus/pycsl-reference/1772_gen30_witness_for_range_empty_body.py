r"""Test 1772 — WITNESS: a `#@ for ... in range(...)` with an EMPTY body.

The sugar exists to expand a clause per value; with no clauses it expands to nothing while
looking like a specification. Refused rather than expanded to silence. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


#@ requires \length(xs) >= 3
#@ for i in range(0, 3):
#@ ensures \result >= 0
def total(xs: List[int]) -> int:
    return xs[0]
