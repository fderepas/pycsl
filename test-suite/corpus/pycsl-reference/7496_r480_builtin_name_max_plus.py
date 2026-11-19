r"""Test 7496 -- route #480 (expected FAIL): `max + n` -- a builtin function NAME used as a value was `val constant max : int`. PROVED at base; CPython TypeError; now REFUSED (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return max + n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
