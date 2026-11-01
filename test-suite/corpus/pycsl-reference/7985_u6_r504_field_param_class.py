r"""Test 7985 -- route #504 (expected FAIL: PROVED at base, REFUSED PYCSL-R504-IS-ON-STORED-VALUE): a class-typed parameter whose int fields are equal, `k.a is k.b` claimed True; CPython returns False with k.b = int("1000") (rt45 g601/b60105)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class K:
    def __init__(self, n: int) -> None:
        self.a = n
        self.b = n


#@ requires k.a == k.b
#@ ensures \result == True
def f(k: K) -> bool:
    return k.a is k.b


if __name__ == "__main__":
    try:
        k = K(1000)
        k.b = int("1000")
        r = f(k)
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
