r"""Test 7921 -- route #499 (expected FAIL: PROVED at base, REFUSED PYCSL-R499-EXEC-IN-FUNCTION-SCOPE): `exec("n += 5")` on a parameter claimed `n + 5`; CPython returns n (rt44 e51701 / e51702)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == n + 5
def f(n: int) -> int:
    exec("n += 5")
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 6):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
