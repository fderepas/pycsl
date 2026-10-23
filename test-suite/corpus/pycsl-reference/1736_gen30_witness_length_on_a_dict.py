r"""Test 1736 — WITNESS for `PYCSL-SEM-PREDBASE`: `\length` on a dict.

Dicts and sets are modelled as TOTAL MAPS, so they have no length to speak of, and the
refusal says what to use instead (`\has_key(d, k)` for presence, a list for a
length-bearing collection). One of the 140 refusals `bin/check-refusal-witness-coverage.py`
measured as having no file proving it can fire.
"""
# pycsl-expected: FAIL
from typing import Dict

_ = 0  # anchor


#@ requires \length(d) >= 0
#@ ensures \result == 0
def f(d: Dict[str, int]) -> int:
    return 0
