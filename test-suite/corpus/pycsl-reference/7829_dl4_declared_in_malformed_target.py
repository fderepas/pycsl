r"""Test 7829 -- cross-mixin-declaration-stubs B4 (expected FAIL: PARSE REFUSAL): `#@ declared_in B.m` omits the `<relpath>.py::` half of the target; the directive's grammar is closed (`declared_in <relpath>.py::<Class>.<method>`), so the contract is refused rather than read as a bare `\trusted`. Without the refusal `f` would prove `\result == 1`; CPython returns 2.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ declared_in B.m
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 2


#@ ensures \result == 1
def f() -> int:
    c = C()
    return c.m()
