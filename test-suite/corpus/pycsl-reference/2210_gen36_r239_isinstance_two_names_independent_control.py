r"""Test 2210 — route #239 (expected FAIL): CONTROL. Two DIFFERENT Any parameters stay
independent (`typeof_op x` vs `typeof_op y`), at base (`typeof_op 120` vs `121`) and after,
so `\result == 1` does not prove; CPython `f(1, "s")` = 0. Localises 2200 to the rebinding.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    a = 0
    if isinstance(x, int):
        a = 1
    b = 0
    if isinstance(y, int):
        b = 1
    if a == b:
        return 1
    return 0
