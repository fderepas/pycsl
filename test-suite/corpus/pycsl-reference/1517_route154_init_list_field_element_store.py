r"""Test 1517 - ROUTE #154 (gen #29): `self.xs = [1, 2]; self.xs[0] = 9` in `__init__` kept route #87's literal and `C().xs[0] == 1` PROVED; CPython 9. A subscript store rooted at `self.<f>` makes the field UNKNOWN.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]
        self.xs[0] = 9


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.xs[0]

