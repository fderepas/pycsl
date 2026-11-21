r"""Test 1648 - ROUTE #183 (gen #29): a field whose only initialiser is the literal `None` (`self.v: Optional[int] = None`) lowered to `{ v = 0 }`, so `c.v == 0` PROVED True (CPython False) - route #56's shape on a FIELD. Such a field now defaults to route #44's opaque `pycsl_none`.
"""
# pycsl-expected: FAIL
from typing import Optional
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v: Optional[int] = None


#@ ensures \result == True
def probe() -> bool:
    c = C()
    return c.v == 0
