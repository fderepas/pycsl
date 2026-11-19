r"""Test 8164 -- route #518 (expected FAIL: PROVED at base, REFUSED PYCSL-R518-WALRUS-AT-DEFINITION-TIME): `_l = lambda a=(inc := dec): a` rebinds the program FUNCTION `inc` (route #118's walk skipped the lambda); `inc(3) == 4` claimed; CPython 2
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

def inc(x: int) -> int:
    return x + 1


def dec(x: int) -> int:
    return x - 1


#@ ensures \result == 4
def f() -> int:
    return inc(3)


_l = lambda a=(inc := dec): a


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 4):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
