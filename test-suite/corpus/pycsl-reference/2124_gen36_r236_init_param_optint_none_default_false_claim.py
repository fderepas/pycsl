r"""Test 2124 — route #236 (expected FAIL): a PLAIN class whose `__init__` takes
`k: Optional[int] = None` and stores `self.k = k`: the omitted parameter is route #149's
`init_default_unknown`, but the `(any int)` it earns was gated to `int`/`bool` fields and the
`_union_*` field kept the definite `0`; `p.k == 0` PROVED, CPython `None`.
"""
# pycsl-expected: FAIL
from typing import Optional


class P:
    def __init__(self, x: int, k: Optional[int] = None) -> None:
        self.x = x
        self.k = k


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.k == 0:
        return 1
    return 2
