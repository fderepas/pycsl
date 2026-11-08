r"""Test 8150 -- route #511 (control, expected PASS): a local class with a unique name, constructed and read inside its function; CPython returns 3
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

#@ ensures \result == 3
def f() -> int:
    class Q:
        def __init__(self, v: int) -> None:
            self.v = v
    q = Q(3)
    return q.v


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 3):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
