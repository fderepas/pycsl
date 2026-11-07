r"""Test 7960 -- route #501 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): a class K defines `index`; g's local `k` is a `str` and calls `k.index("z")` (the `k__index` spelling of the method); f catches ValueError; CPython returns 2
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional

class K:
    #@ ensures \result == 0
    def index(self, x: int) -> int:
        return 0


#@ ensures \result == 1
def g(s: str) -> int:
    k = s + "b"
    y = k.index("z")
    return 1


#@ ensures \result == 1
def f(s: str) -> int:
    try:
        return g(s)
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f("a")
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
