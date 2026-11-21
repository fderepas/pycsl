r"""Test 7924 -- route #499 (expected FAIL: PROVED at base, REFUSED PYCSL-R499-EXEC-IN-FUNCTION-SCOPE): `exec("y = 6"); return y` in a function claimed 6 (the old 0642 shape); CPython raises NameError (y is a global read, never bound)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == 6
def f() -> int:
    exec("y = 6")
    return y


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 6):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
