r"""Test 1779 — WITNESS: a NESTED `Literal[Literal[1]]`.

L4 / L5c / PEP 586. PEP 586 flattens nested Literals; this lowering does not, so accepting
one would silently model a different type from the one Python means. Refused. One of the
refusals `bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import Literal

_ = 0  # anchor


#@ ensures \result >= 0
def pick(x: Literal[Literal[1]]) -> int:
    return 0
