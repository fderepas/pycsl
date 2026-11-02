r"""Test 8147 -- route #511 (expected FAIL: PROVED at base, REFUSED PYCSL-R511-LOCAL-CLASS-NAME-NOT-UNIQUE): `K = 5`, then a function-local `type K = int` statement and `return K` under `ensures \result == 5`; the alias statement is not lowered and K stayed folded; CPython returns the TypeAliasType
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5


#@ ensures \result == 5
def f() -> int:
    type K = int
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
