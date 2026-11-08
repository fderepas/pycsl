r"""Test 1768 — WITNESS: an unsupported `.method()` call inside a CONTRACT.

Only `.keys()`, `.values()` and `.items()` are recognised on a dict in contract position
(07-1311); anything else would be parsed into a shape the contract language has no meaning
for. Refused at the contract parser. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import Dict

_ = 0  # anchor


#@ requires d.clear() != 0
#@ ensures \result >= 0
def peek(d: Dict[int, int]) -> int:
    return 0
