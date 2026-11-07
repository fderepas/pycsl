r"""Test 2110 — route #236 (expected FAIL): a `@dataclass` field `k: Optional[int] = None`
OMITTED at construction. At base the class-body collector `pass`ed the `None` default and the
record literal took the DEFINITE `0`, so `p.k == 0` was decided True and `\result == 1` PROVED
(CPython: `None == 0` is False, `g(5)` returns 2). The field is now route #44's opaque
`pycsl_none`: the comparison is undecided. Control: 2127.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Optional


@dataclass
class P:
    x: int
    k: Optional[int] = None


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.k == 0:
        return 1
    return 2
