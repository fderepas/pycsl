r"""Test 9683 -- route #598 (expected FAIL: PROVED at base bfe0e38fb in the default model, REFUSED PYCSL-R598-RAISE-CONSTRUCTOR-ARITY in every model at HEAD): red team rt57 (family F3, bare raise of a class with a required argument): a bare `raise E` of a `class E(Exception)` whose `__init__(self, a)` needs an argument (CPython calls `E()`); CPython raises TypeError under `no_exception \all`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional

class E(Exception):
    def __init__(self, a: str) -> None:
        self.a = a


#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    try:
        raise E
    except E:
        return 1
    return 2


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
