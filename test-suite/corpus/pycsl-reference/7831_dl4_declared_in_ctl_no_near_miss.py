r"""Test 7831 -- cross-mixin-declaration-stubs B4 (control, expected PASS): witness 7830 with the near-miss `# @declared_in other.py::B.m` comment line deleted; every contract is true (`m` returns 1) and the file proves, so 7830's FAIL is the near-miss refusal alone; CPython returns 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


#@ ensures \result == 1
def f() -> int:
    c = C()
    return c.m()
