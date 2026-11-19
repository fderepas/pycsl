r"""Test 7989 -- route #504 (expected FAIL: PROVED at base, REFUSED PYCSL-R504-IS-ON-STORED-VALUE): a computed int field against a module global literal, `k.a is G` with `G = 1000`, `self.a = n + 1000`, `requires n == 0`, claimed True; CPython f(0) returns False (an outer-name operand is no exemption)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


G = 1000


class K:
    def __init__(self, n: int) -> None:
        self.a = n + 1000


#@ requires n == 0
#@ ensures \result == True
def f(n: int) -> bool:
    k = K(n)
    return k.a is G


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
