r"""Test 9955 -- route #602 (expected FAIL: PROVED at L9 and at base 73fd1874f, REFUSED PYCSL-R602-HANDLER-NAME-REBOUND at HEAD): rt58 d08: `Err = ValueError` then `except Err:` lowered to a fresh `exception Err`, so the raised ValueError escaped; `f(1)` returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations

Err = ValueError


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    x = 0
    try:
        if n > 0:
            raise ValueError("v")
        x = 0
    except Err:
        x = 1
    return x


if __name__ == "__main__":
    r = f(1)
    print("VIOLATION contract" if r != 0 else "result", r)
