r"""Test 1518 - ROUTE #154 (gen #29): `self.d = {1: 5}; self.d[1] = 9` kept route #85's literal and `C().d[1] == 5` PROVED; CPython 9.
"""
# pycsl-expected: FAIL
from typing import Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.d: Dict[int, int] = {1: 5}
        self.d[1] = 9


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.d[1]

