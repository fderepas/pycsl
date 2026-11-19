r"""Test 9956 -- route #602 (expected FAIL: PROVED at base 952bf7891 in the default model, full proof; REFUSED PYCSL-R602-HANDLER-NAME-REBOUND at HEAD): the alias is a LOCAL of the function (`Err = ValueError` in the body); `f(1)` returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    Err = ValueError
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
