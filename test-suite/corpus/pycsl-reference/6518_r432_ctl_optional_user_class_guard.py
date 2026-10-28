r"""Test 6518 -- route #432 (expected PASS): CONTROL: a guarded user method on `Optional[C]` is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Optional

class C:
    def __init__(self) -> None:
        self.k: int = 1
    def m(self) -> int:
        return 2


#@ no_exception \all
def f(c: Optional[C]) -> int:
    if c is not None:
        return c.m()
    return 0
