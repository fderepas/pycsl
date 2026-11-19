r"""Test 9948 -- route #599 (expected FAIL: PROVED at base 952bf7891 in the default model, full proof; REFUSED PYCSL-R599-HANDLER-UNMODELLED-RAISER at HEAD): an explicit `raise TypeError` covers `except TypeError`, then `a + 1` on an `Any` holding a str raises it (an operator); returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(a: Any, n: int) -> int:
    x = 0
    try:
        if n > 100:
            raise TypeError("u")
        x = 1
        y = a + 1
    except TypeError:
        return x
    return 0


if __name__ == "__main__":
    r = f("s", 0)
    print("VIOLATION contract" if r != 0 else "result", r)
