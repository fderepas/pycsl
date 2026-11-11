r"""Test 9520 -- lvP cap-trusted-val-unit-return (expected FAIL): the unpacked first component of the
UNCONSTRAINED trusted tuple is arbitrary, so `\result == "x"` must NOT prove (CPython: "p").
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List, Tuple


def mutable_state(cls): return cls


@mutable_state
class B:
    def __init__(self) -> None:
        self.i = 0

    #@ \trusted reviewer: lvp-witness
    #@ assigns self.i
    def pair(self) -> Tuple[str, List[Tuple[str, "ExprIR"]]]:
        pass

    #@ ensures \result == "x"
    #@ assigns self.i
    def name(self) -> str:
        n, rs = self.pair()
        return n



if __name__ == "__main__":
    # one implementation the trusted contract admits (the stub body is `pass`)
    n, rs = ("p", [("r", 1)])
    r = n
    print("VIOLATION contract" if r != "x" else "result", r)
