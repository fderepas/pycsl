r"""Test 1794 — WITNESS: a list literal mixing tuple arities.

07-0903 W1. A list of tuples lowers to a faithful `array (t0, ...)` — each element a Why3
TUPLE, not collapsed to an int — and that needs ONE uniform element type. A literal whose
tuples have different arities has no such type, so it is refused rather than collapsed.
One of the refusals `bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import List, Tuple

_ = 0  # anchor


#@ ensures \result >= 0
def build() -> int:
    xs: List[Tuple[int, int]] = [(1, 2), (3, 4, 5)]
    return 0
