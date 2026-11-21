r"""Test 8151 -- route #511 (control, expected PASS): two functions each with their own local class under DISTINCT names, beside a module constant of a third name; CPython returns 5
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5


def mk() -> int:
    class P:
        pass
    return 0


#@ ensures \result == 5
def f() -> int:
    class Q:
        pass
    return K


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 5):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
