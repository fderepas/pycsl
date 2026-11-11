r"""Test 9515 -- lvP cap-vm-unerase-tuple (expected PASS): the `_parse_inductive` member shape. A
`(name, signature, rules)` triple whose third slot is itself a `List[Tuple[str, "ExprIR"]]` is a native
`(string, string, seq (string, emit_ir))` element (the inner list is the PURE `seq`: an `array` component
cannot sit in a `seq`), returned as the `seq` of triples; the loop binds `sig` to the appended literal.
Twin: 9516.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List, Tuple


def mutable_state(cls): return cls


@mutable_state
class B:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def rules(self, n: str, e: "ExprIR") -> List[Tuple[str, "ExprIR"]]:
        rs = []
        rs.append((n, e))
        return rs

    #@ sibling_concrete
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def members(self, n: str, e: "ExprIR") -> List[Tuple[str, str, List[Tuple[str, "ExprIR"]]]]:
        out = []
        wr = self.rules(n, e)
        out.append((n, "()", wr))
        for nm, sig, rr in out:
            #@ assert sig == "()"
            pass
        return out


if __name__ == "__main__":
    r = B().members("q", 7)
    print("VIOLATION" if r[0][1] != "()" else "result", r)
