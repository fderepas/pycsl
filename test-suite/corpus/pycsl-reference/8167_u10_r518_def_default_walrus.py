r"""Test 8167 -- route #518 (expected FAIL: REFUSED at base by route #350, now REFUSED PYCSL-R518-WALRUS-AT-DEFINITION-TIME): the same walrus in a module `def`'s default (the def twin, refused before by route #350, now by the definition-time rule); CPython returns 0
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5


#@ ensures \result == 5
def f() -> int:
    return K


def _d(a: int = (K := 0)) -> int:
    return a


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 5):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
