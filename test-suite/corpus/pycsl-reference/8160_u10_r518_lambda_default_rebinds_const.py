r"""Test 8160 -- route #518 (expected FAIL: PROVED at base, REFUSED PYCSL-R518-WALRUS-AT-DEFINITION-TIME): `K = 5`, `ensures \result == 5` over `return K`, then `_l = lambda a=(K := 0): a` at module level rebinds K when the lambda is created; CPython returns 0
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5


#@ ensures \result == 5
def f() -> int:
    return K


_l = lambda a=(K := 0): a


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 5):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
