r"""Test 9519 -- lvP cap-trusted-val-unit-return (expected PASS): a `\trusted` `pass`-body method declared
`-> Tuple[str, List[Tuple[str, "ExprIR"]]]` is announced with its native tuple type `(string, seq (string,
emit_ir))` instead of `unit`; a verified caller unpacks it (`n, rs = self.pair()`: the zero-argument receiver
val is no longer curried over `()`, and `rs` is pre-declared a tuple-element seq) and `len(rs) >= 0` proves.
Twin: 9520.
"""
# pycsl-expected: PASS
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
    def pair(self) -> Tuple[str, List[Tuple[str, "ExprIR"]]]:
        pass

    #@ requires True
    #@ ensures \result >= 0
    #@ assigns self.i
    def count(self) -> int:
        n, rs = self.pair()
        return len(rs)



if __name__ == "__main__":
    # one implementation the trusted contract admits (the stub body is `pass`)
    n, rs = ("p", [("r", 1)])
    r = len(rs)
    print("VIOLATION" if r < 0 else "result", r)
