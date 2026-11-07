r"""Test 7497 -- route #480 (expected FAIL): `1 if NotImplemented else 0` -- the truth value of NotImplemented raises TypeError (CPython 3.14). PROVED at base; now REFUSED (R325).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return 1 if NotImplemented else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
