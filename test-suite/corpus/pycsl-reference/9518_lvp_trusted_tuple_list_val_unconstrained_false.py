r"""Test 9518 -- lvP cap-trusted-val-unit-return (expected FAIL): the trusted val's result is
UNCONSTRAINED (no ensures is added by the typing), so `\result == 0` must NOT prove (CPython: 1).
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
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def rules(self) -> List[Tuple[str, "ExprIR"]]:
        pass

    #@ requires True
    #@ ensures \result == 0
    #@ assigns self.i
    def count(self) -> int:
        rs = self.rules()
        return len(rs)



if __name__ == "__main__":
    # one implementation the trusted contract admits (the stub body is `pass`)
    rs = [("r", 1)]
    r = len(rs)
    print("VIOLATION contract" if r != 0 else "result", r)
