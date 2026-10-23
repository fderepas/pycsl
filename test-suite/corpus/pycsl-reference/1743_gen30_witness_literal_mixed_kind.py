r"""Test 1743 — WITNESS: a `Literal[...]` mixing kinds.

`Literal[1, "a"]` puts an int and a str in one value set. PEP 586 allows it; PyCSL does
not model it, and refuses rather than picking one. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness. Sibling: 1744 (a
float literal, which PEP 586 itself excludes).
"""
# pycsl-expected: FAIL
from typing import Literal

_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == 0
def f(n: int, m: Literal[1, "a"]) -> int:
    return 0
