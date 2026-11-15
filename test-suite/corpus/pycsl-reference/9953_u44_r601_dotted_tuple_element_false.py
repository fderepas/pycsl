r"""Test 9953 -- route #601 (expected FAIL: PROVED at L9 and at base 73fd1874f, REFUSED PYCSL-R601-HANDLER-TUPLE-NON-NAME at HEAD): rt58 d07: `except (ZeroDivisionError, builtins.ValueError)` lowered to `with ZeroDivisionError` (the dotted element dropped), so the raised ValueError escaped in the model; `f(1)` returns 7 under `ensures \result == 2`
"""
# pycsl-expected: FAIL
from __future__ import annotations
import builtins


#@ ensures \result == 2
#@ assigns \nothing
def f(n: int) -> int:
    x = 0
    try:
        if n > 0:
            raise ValueError("v")
        x = 2
    except (ZeroDivisionError, builtins.ValueError):
        x = 7
    return x + 0 * n


if __name__ == "__main__":
    r = f(1)
    print("VIOLATION contract" if r != 2 else "result", r)
