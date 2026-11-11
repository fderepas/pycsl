r"""Test 9516 -- lvP cap-vm-unerase-tuple (expected FAIL): false twin of 9515: `nm` is the appended `n`,
so `#@ assert nm == "zz"` must NOT prove (CPython: "q").
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List, Tuple


def mutable_state(cls): return cls


@mutable_state
class B:
    #@ assigns \nothing
    def rules(self, n: str, e: "ExprIR") -> List[Tuple[str, "ExprIR"]]:
        rs = []
        rs.append((n, e))
        return rs

    #@ assigns \nothing
    def members(self, n: str, e: "ExprIR") -> List[Tuple[str, str, List[Tuple[str, "ExprIR"]]]]:
        out = []
        wr = self.rules(n, e)
        out.append((n, "()", wr))
        for nm, sig, rr in out:
            #@ assert nm == "zz"
            pass
        return out


if __name__ == "__main__":
    r = B().members("q", 7)
    print("VIOLATION assert" if r[0][0] != "zz" else "result", r)
