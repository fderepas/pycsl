r"""Test 7827 -- cross-mixin-declaration-stubs B4 (expected FAIL: REFUSED, `#@ declared_in` outside the self-annotation mirror): `C.m` carries `#@ declared_in other.py::B.m` and a false `ensures \result == 1` (its body returns 2). `declared_in` parses to the same node as `\trusted`; outside src/self-annotate/src/ nothing certifies the declaration, so pycsl refuses it instead of letting it act as an unreviewed `\trusted`. Without the refusal `f` would prove `\result == 1`; CPython returns 2.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ declared_in other.py::B.m
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 2


#@ ensures \result == 1
def f() -> int:
    c = C()
    return c.m()
