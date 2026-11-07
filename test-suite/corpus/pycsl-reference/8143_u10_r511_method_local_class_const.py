r"""Test 8143 -- route #511 (expected FAIL: PROVED at base, REFUSED PYCSL-R511-LOCAL-CLASS-NAME-NOT-UNIQUE): a class statement inside a METHOD shadows the module constant `K`; `ensures \result == 5` over `return K`; CPython returns the class
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5


class Box:
    #@ ensures \result == 5
    def m(self) -> int:
        class K:
            pass
        return K


def f() -> int:
    return Box().m()


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 5):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
