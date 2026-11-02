r"""Test 8163 -- route #518 (expected FAIL: PROVED at base, REFUSED PYCSL-R518-WALRUS-AT-DEFINITION-TIME): `S = "ab"`, `len(S) == 2` claimed, then `_l = lambda a=(S := "abc"): a`; CPython returns 3
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

S = "ab"


#@ ensures \result == 2
def f() -> int:
    return len(S)


_l = lambda a=(S := "abc"): a


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
