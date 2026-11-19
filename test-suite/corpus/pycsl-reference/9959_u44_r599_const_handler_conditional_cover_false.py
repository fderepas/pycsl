r"""Test 9959 -- route #599 (expected FAIL: PROVED at base 952bf7891 in the default model, full proof; REFUSED PYCSL-R599-HANDLER-UNMODELLED-RAISER at HEAD): the boundary of the state-insensitive-handler exemption -- the handler is a constant `return 1`, but its only cover is a CONDITIONAL `raise OSError` (`n > 100`, excluded by `requires n <= 100`), so the model proves the handler dead while `os.path.getsize(s)` reaches it in CPython; returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations
import os


#@ requires n <= 100
#@ ensures \result == 0
#@ assigns \nothing
def f(s: str, n: int) -> int:
    try:
        if n > 100:
            raise OSError("u")
        k = os.path.getsize(s)
    except OSError:
        return 1
    return 0


if __name__ == "__main__":
    r = f("/no/such/u44", 0)
    print("VIOLATION contract" if r != 0 else "result", r)
