r"""Test 8165 -- route #518 (expected FAIL: NOT PROVED at base (opaque read), REFUSED by name PYCSL-R518-WALRUS-AT-DEFINITION-TIME): a class-body `_l = lambda a=(K := 0): a` rebinds the class constant `C.K`; `C.K == 5` claimed; CPython 0
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

class C:
    K = 5
    _l = lambda a=(K := 0): a


#@ ensures \result == 5
def f() -> int:
    return C.K


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 5):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
