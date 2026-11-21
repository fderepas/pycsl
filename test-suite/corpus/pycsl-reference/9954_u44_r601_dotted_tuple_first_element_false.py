r"""Test 9954 -- route #601 (expected FAIL: PROVED at base 952bf7891 in the default model, full proof; REFUSED PYCSL-R601-HANDLER-TUPLE-NON-NAME at HEAD): the dotted element FIRST in the tuple, `except (builtins.ValueError, ZeroDivisionError)`; `f(1)` returns 7 under `ensures \result == 2`
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
    except (builtins.ValueError, ZeroDivisionError):
        x = 7
    return x + 0 * n


if __name__ == "__main__":
    r = f(1)
    print("VIOLATION contract" if r != 2 else "result", r)
