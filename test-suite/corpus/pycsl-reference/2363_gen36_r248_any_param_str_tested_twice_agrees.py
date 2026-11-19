r"""Test 2363 — route #248 (expected PASS): CONTROL. A program-side `str` test on an unrebound `Any`
parameter is keyed on the parameter's identity (`typeof_op "pycsl_param_tag:f:x"`), one Python object
per invocation, so two tests agree and `\result == 1` PROVES (CPython: 1 for any `x`).
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    a = 0
    if isinstance(x, str):
        a = 1
    b = 0
    if isinstance(x, str):
        b = 1
    if a == b:
        return 1
    return 0


if __name__ == "__main__":
    assert f("s") == 1 and f(1) == 1 and f([]) == 1
