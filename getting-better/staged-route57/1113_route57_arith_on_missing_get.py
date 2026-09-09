"""Test 1113 — ROUTE #57 negative witness (b): ARITHMETIC on a missing `.get`, the
shape where the model does not merely compare `None` to zero but COMPUTES with it.

FALSE OF THE PROGRAM: Python raises
`TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'`. It does not
return 1; it does not return at all.

At the parent commit this proved `\\result == 1`, because the `| None ->` arm of the
`.get` read answered the codomain's zero and `0 + 1 = 1`. A program that CRASHES was
given a total, decided, wrong answer.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 2}
    v = d.get(5)
    return v + 1
