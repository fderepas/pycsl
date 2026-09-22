r"""Test 1791 — WITNESS: `\forall x in d.items()`, the two-binder form.

07-1311 follow-on. `.keys()` and `.values()` each bind ONE variable and desugar to a
membership or an existential; `.items()` would need TWO binders and there is no desugaring
for it, so it is refused with the two supported spellings named. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import Dict

_ = 0  # anchor


#@ requires \forall x in d.items(); x >= 0
#@ ensures \result >= 0
def total(d: Dict[int, int]) -> int:
    return 0
