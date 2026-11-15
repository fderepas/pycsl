r"""Test 9942 -- route #599 (expected FAIL: PROVED at L9 AND at the pre-run base 73fd1874f, REFUSED PYCSL-R599-HANDLER-UNMODELLED-RAISER at HEAD): rt58 c06b, the pre-existing twin: an explicit `raise OSError` covers `except OSError`, then `os.path.getsize(s)` raises it only in CPython; returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations
import os


#@ ensures \result == 0
#@ assigns \nothing
def f(s: str, n: int) -> int:
    x = 0
    try:
        if n > 100:
            raise OSError("u")
        x = 1
        k = os.path.getsize(s)
    except OSError:
        return x
    return 0


if __name__ == "__main__":
    r = f("/no/such/rt58", 0)
    print("VIOLATION contract" if r != 0 else "result", r)
