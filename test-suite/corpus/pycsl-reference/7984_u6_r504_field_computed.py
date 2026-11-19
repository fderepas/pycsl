r"""Test 7984 -- route #504 (expected FAIL: PROVED at base, REFUSED PYCSL-R504-IS-ON-STORED-VALUE): `self.a = n + 1000; self.b = n + 1000`, `k.a is k.b` claimed True; CPython f(5) returns False (rt45 g601/b60104)
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
    return k.a is k.b


if __name__ == "__main__":
    try:
        r = f(5)
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
