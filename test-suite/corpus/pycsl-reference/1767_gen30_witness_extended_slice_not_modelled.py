r"""Test 1767 — WITNESS: an EXTENDED slice `x[lo:hi:step]`, whose step the lowering drops.

The lowering is `Array.sub x lo (hi - lo)`, which ignores `step` entirely, so the model
would carry a DIFFERENT sequence — different length and different elements — from the one
Python builds. Refused rather than lowered. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


#@ requires \length(xs) >= 4
#@ ensures \result >= 0
def every_other(xs: List[int]) -> int:
    ys = xs[0:4:2]
    return ys[0]
