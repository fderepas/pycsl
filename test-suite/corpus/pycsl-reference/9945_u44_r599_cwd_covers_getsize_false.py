r"""Test 9945 -- route #599 (expected FAIL: PROVED at L9, REFUSED PYCSL-R599-HANDLER-UNMODELLED-RAISER at HEAD): rt58 c14b: the modelled `Path.cwd()` covers `except OSError`, then `os.path.getsize(s)` raises it only in CPython; returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations
import os
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def f(s: str) -> int:
    x = 0
    try:
        Path.cwd()
        x = 1
        k = os.path.getsize(s)
    except OSError:
        return x
    return 0


if __name__ == "__main__":
    r = f("/no/such/rt58")
    print("VIOLATION contract" if r != 0 else "result", r)
