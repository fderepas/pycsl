r"""Test 1792 — WITNESS: a `Callable[...]` annotation that is not the two-part form.

`PYCSL-TY3-CALLABLE-SCOPE` (C5 sound scope limit, stricter than S1). A Callable annotation
must be `Callable[[A1, ..., An], R]` — an arg LIST and a return. A subscript that is not
that 2-tuple encodes a signature the model cannot describe, so it is a loud fail rather
than a guess. NOTE the near miss: `Callable[..., int]` IS a 2-tuple and lands on the NEXT
refusal ("first argument must be a literal list"), which is why this witness uses the
single-element form. One of the refusals `bin/check-refusal-witness-coverage.py` measured
as having no witness.
"""
# pycsl-expected: FAIL
from typing import Callable

_ = 0  # anchor


#@ ensures \result >= 0
def apply(f: Callable[int]) -> int:
    return 0
