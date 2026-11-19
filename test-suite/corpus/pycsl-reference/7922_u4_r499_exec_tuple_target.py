r"""Test 7922 -- route #499 (expected FAIL: PROVED at base, REFUSED PYCSL-R499-EXEC-IN-FUNCTION-SCOPE): `exec("a, b = 3, 4")` over locals claimed 7; CPython returns 0 (rt44 e51717)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == 7
def f(n: int) -> int:
    a = 0
    b = 0
    exec("a, b = 3, 4")
    return a + b


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 7):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
