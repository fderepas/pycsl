r"""Test 9267 -- route #578 (expected FAIL: PROVED at base `no_exception \all`, NOT PROVED: route #252's obligation, now also at
a power op on an erased operand): `x: Any`; `v = x ** 2`; CPython f(None) TypeError unsupported operand type(s) for ** or
pow(): 'NoneType' and 'int'.
"""
# pycsl-expected: FAIL
from typing import Any


#@ no_exception \all
def f(x: Any, k: int) -> int:
    v = x ** 2
    return 0


if __name__ == "__main__":
    try:
        print("result", f(None, 1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
