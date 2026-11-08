r"""Test 2330 — route #246 (expected PASS): CONTROL. Two `float` tests of ONE unrebound parameter
agree: the tag is keyed on the PARAMETER's identity (`typeof_op "pycsl_param_tag:f:x"`), one Python
object for the whole invocation, so `\result == 1` PROVES (CPython: 1 for any `x`).
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    a = 0
    if isinstance(x, float):
        a = 1
    b = 0
    if isinstance(x, float):
        b = 1
    if a == b:
        return 1
    return 0


if __name__ == "__main__":
    assert f(1) == 1 and f(1.0) == 1 and f("s") == 1
