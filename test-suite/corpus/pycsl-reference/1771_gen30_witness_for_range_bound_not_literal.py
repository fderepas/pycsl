r"""Test 1771 — WITNESS: a `#@ for ... in range(...)` whose bound is not an integer literal.

The `#@ for` sugar EXPANDS into one clause per value, so the bound must be resolvable at
weave time. v1 accepts an integer literal only, and anything else is a hard, fail-loud
error — never a silent fallback (sugar-for-spec.md §5.1). One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor

N = 3


#@ requires \length(xs) >= 3
#@ for i in range(0, N):
#@     requires xs[i] >= 0
#@ ensures \result >= 0
def total(xs: List[int]) -> int:
    return xs[0]
