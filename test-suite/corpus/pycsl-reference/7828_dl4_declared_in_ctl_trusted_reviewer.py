r"""Test 7828 -- cross-mixin-declaration-stubs B4 (control, expected PASS): witness 7827 with `#@ declared_in other.py::B.m` replaced by the spelling the refusal advises, `#@ \trusted reviewer: dl4-control`, and an honest body (`m` returns 1); the trusted stub is accepted and counted in the trusted base; CPython returns 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ \trusted reviewer: dl4-control
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


#@ ensures \result == 1
def f() -> int:
    c = C()
    return c.m()
