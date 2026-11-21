r"""Test 8152 -- route #511 (control, expected PASS): a function-local `type Pair = ...` statement with a unique name, unread as a value; CPython returns 5
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5


#@ ensures \result == 5
def f() -> int:
    type Pair = tuple[int, int]
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
