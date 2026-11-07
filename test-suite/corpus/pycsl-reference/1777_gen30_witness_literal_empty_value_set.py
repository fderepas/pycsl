r"""Test 1777 — WITNESS: `Literal[()]`, an EMPTY literal value set.

L1 / PEP 586. A `Literal` with no values denotes the empty type — nothing inhabits it — so
lowering it would produce a variable whose type no value satisfies while the program keeps
assigning to it. Refused. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import Literal

_ = 0  # anchor


#@ ensures \result >= 0
def pick(x: Literal[()]) -> int:
    return 0
