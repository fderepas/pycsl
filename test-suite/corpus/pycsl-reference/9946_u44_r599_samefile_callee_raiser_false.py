r"""Test 9946 -- route #599 (expected FAIL: PROVED at base 952bf7891 in the default model, full proof; REFUSED PYCSL-R599-HANDLER-UNMODELLED-RAISER at HEAD): an explicit `raise OSError` covers `except OSError`, then a SAME-FILE callee `g` (no `raises`) runs `os.path.getsize`, which raises OSError out of it only in CPython; returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations
import os


#@ assigns \nothing
def g(s: str) -> int:
    return os.path.getsize(s)


#@ ensures \result == 0
#@ assigns \nothing
def f(s: str, n: int) -> int:
    x = 0
    try:
        if n > 100:
            raise OSError("u")
        x = 1
        k = g(s)
    except OSError:
        return x
    return 0


if __name__ == "__main__":
    r = f("/no/such/u44", 0)
    print("VIOLATION contract" if r != 0 else "result", r)
