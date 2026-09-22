r"""Test 1734 — WITNESS for `PYCSL-SEM-ASSIGNS`: an assigns REGION naming a variable that
does not exist.

`#@ assigns a[0..k]` where `k` is not a parameter, a local or a module name. A frame that
names nothing is not a frame, and a typo in one is silent otherwise. One of the 140
refusals that `bin/check-refusal-witness-coverage.py` measured as having no witness.
Sibling: 1735 (a region on a NON-LIST variable).
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


#@ requires \length(a) >= 1
#@ assigns a[0..k]
def f(a: List[int]) -> None:
    a[0] = 1
