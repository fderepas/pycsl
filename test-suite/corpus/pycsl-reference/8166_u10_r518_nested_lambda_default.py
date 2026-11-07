r"""Test 8166 -- route #518 (expected FAIL: PROVED at base, REFUSED PYCSL-R518-WALRUS-AT-DEFINITION-TIME): a lambda in ANOTHER lambda's default: `lambda a=(lambda b=(K := 0): b): a`; CPython returns 0
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5


#@ ensures \result == 5
def f() -> int:
    return K


_l = lambda a=(lambda b=(K := 0): b): a


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 5):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
