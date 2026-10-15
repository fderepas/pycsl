r"""Test 2200 — route #239 (expected FAIL): `isinstance(<Any>, T)` was keyed on the variable's
NAME. Both tests lowered to `(typeof_op 120)` (120 = the code points of `x`), a pure `val
function` of a constant, so rebinding `x = y` could not change the answer and `\result == 1`
PROVED at f926a808 while CPython `f(1, "s")` = 0. The tag is now `typeof_op` APPLIED TO THE
CURRENT VALUE (`typeof_op !x`), so the two tests are unrelated. Controls: 2210, 2211.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    a = 0
    if isinstance(x, int):
        a = 1
    x = y
    b = 0
    if isinstance(x, int):
        b = 1
    if a == b:
        return 1
    return 0
