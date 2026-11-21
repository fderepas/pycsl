r"""Test 8161 -- route #518 (expected FAIL: PROVED at base, REFUSED PYCSL-R518-WALRUS-AT-DEFINITION-TIME): the keyword-only default `lambda *, a=(K := 0): a`, before the claimed def; CPython returns 1
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5
_l = lambda *, a=(K := 0): a


#@ ensures \result == 6
def f() -> int:
    return K + 1


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 6):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
