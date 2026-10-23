r"""Test 1740 — WITNESS: a dict method other than `.keys()`/`.values()` inside a contract.

Contracts see dicts as total maps, so `d.items()` has no meaning there and the parser
refuses it by name. One of the refusals `bin/check-refusal-witness-coverage.py` measured as
having no file proving it can fire.
"""
# pycsl-expected: FAIL
from typing import Dict

_ = 0  # anchor


#@ requires \has_key(d, "a")
#@ ensures \result == 0
def f(d: Dict[str, int]) -> int:
    #@ check \length(d.items()) >= 0
    return 0
