r"""Test 1307 — ROUTE #111 negative witness, CALL-VALUED RHS: `self.b = mk()` where `mk`
returns `Dict[int, int]` was replaced by the EVERYWHERE-EMPTY MAP, although `mk` itself is
emitted `let mk () : map int (option int)` — a well-typed value discarded by a text test.

FALSE OF THE PROGRAM: `mk()` returns `{1: 5}`, CPython returns 1. At the parent commit the
false `\result == 0` PROVED (rc=0). The store is now `self.b <- (mk ())` and the claim is
refused on the method's postcondition.
"""
# pycsl-expected: FAIL
from typing import Dict

#@ ensures True
def mk() -> Dict[int, int]:
    return {1: 5}

class C:
    b: Dict[int, int]
    #@ assigns self.b
    def __init__(self) -> None:
        self.b = {}

    #@ ensures \result == 0
    #@ assigns self.b
    def put_and_check(self) -> int:
        self.b = mk()
        if 1 in self.b:
            return 1
        return 0


def f() -> int:
    c = C()
    return c.put_and_check()
