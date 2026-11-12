r"""Test 9517 -- lvP cap-trusted-val-unit-return (expected PASS): a `\trusted` `pass`-body method declared
`-> List[Tuple[str, "ExprIR"]]` is announced as an UNCONSTRAINED `seq (string, emit_ir)` (was `array int` of
erased elements); a verified caller's `len(rs) >= 0` proves from the seq length alone. Twin: 9518.
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
    #@ assigns self.i
    def rules(self) -> List[Tuple[str, "ExprIR"]]:
        pass

    #@ ensures \result >= 0
    #@ assigns self.i
    def count(self) -> int:
        rs = self.rules()
        return len(rs)



if __name__ == "__main__":
    # one implementation the trusted contract admits (the stub body is `pass`)
    rs = [("r", 1)]
    r = len(rs)
    print("VIOLATION" if r < 0 else "result", r)
