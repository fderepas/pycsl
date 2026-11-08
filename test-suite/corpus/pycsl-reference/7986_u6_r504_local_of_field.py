r"""Test 7986 -- route #504 (expected FAIL: PROVED at base, REFUSED PYCSL-R504-IS-ON-STORED-VALUE): locals bound to two int field reads, `x = k.a; y = k.b; return x is y` claimed True; CPython f(5) returns False
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class K:
    def __init__(self, n: int) -> None:
        self.a = n + 1000
        self.b = n + 1000


#@ ensures \result == True
def f(n: int) -> bool:
    k = K(n)
    x = k.a
    y = k.b
    return x is y


if __name__ == "__main__":
    try:
        r = f(5)
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
