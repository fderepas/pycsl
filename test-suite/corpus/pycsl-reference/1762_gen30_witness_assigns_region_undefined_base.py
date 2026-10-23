r"""Test 1762 — WITNESS: an `#@ assigns` REGION whose base variable does not exist.

`PYCSL-SEM-ASSIGNS`. A region target `xs[a .. b]` names an array base; if the symbol table
has no such variable the frame would speak about nothing while looking like a frame, so it
is refused. One of the refusals `bin/check-refusal-witness-coverage.py` measured as having
no witness.
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


#@ requires \length(xs) > 4
#@ assigns ys[0 .. 2]
def zero_prefix(xs: List[int]) -> None:
    xs[0] = 0
