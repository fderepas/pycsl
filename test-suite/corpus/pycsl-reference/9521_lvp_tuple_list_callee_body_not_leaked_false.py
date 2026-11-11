r"""Test 9521 -- lvP cap-vm-unerase-tuple (expected FAIL): MODULARITY. A caller of a VERIFIED
`-> List[Tuple[str, "ExprIR"]]` sibling (concrete-called, `#@ sibling_concrete`) sees only the callee's
CONTRACT (`ensures True`), never its body: the components of the returned seq are unknown to it, so
`#@ assert nm == n` must NOT prove although CPython satisfies it -- the claim is not entailed by the
contract (a proof here would mean the callee's body leaked through the new `seq` return).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List, Tuple


def mutable_state(cls): return cls


@mutable_state
class B:
    #@ sibling_concrete
    #@ assigns \nothing
    def build(self, n: str, e: "ExprIR") -> List[Tuple[str, "ExprIR"]]:
        rules = []
        rules.append((n, e))
        return rules

    #@ assigns \nothing
    def first(self, n: str, e: "ExprIR") -> int:
        rs = self.build(n, e)
        for nm, ex in rs:
            #@ assert nm == n
            pass
        return 0


if __name__ == "__main__":
    print("result", B().first("a", 1))
