r"""Test 1793 — WITNESS: `isinstance(x, Literal[...])`.

LR4 / PEP 586. A `typing.Literal` alias is not a valid second argument to `isinstance`:
`Literal` denotes a set of VALUES, not a runtime class, and the shim must not make it one —
a would-be membership test would surface as an unconstrained boolean (a solver timeout at
best). Refused, with the repair named: a concrete value equality test. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import Literal

_ = 0  # anchor


#@ ensures \result >= 0
def check(x: int) -> int:
    if isinstance(x, Literal[1]):
        return 1
    return 0
