r"""Test 7961 -- route #501 (expected FAIL: already REFUSED at base (route #496); REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL by the resolver: a rebound local is unresolved): g binds `k = K()` and then rebinds `k` to a `str` before `k.index("z")` (a class K defines `index`); f catches ValueError; CPython returns 2
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional

class K:
    #@ ensures \result == 0
    def index(self, x: str) -> int:
        return 0


#@ ensures \result == 1
def g(s: str) -> int:
    k: Any = K()
    k = s
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
