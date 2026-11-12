r"""Test 9523 -- lvP cap-vm-unerase-tuple (expected PASS): a VERIFIED `-> Tuple[str, List[str]]` method (the `_parse_variant_def` shape: a call-valued first slot, a list of names) returns its DECLARED tuple `(string, array string)`; at base the body-inferred `(int, array int)` (a call-valued slot) did not type-check against the string slot. `\result[0] == n` proves through the callee contract. Twin: 9524.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List, Tuple


def mutable_state(cls): return cls


@mutable_state
class B:
    #@ sibling_concrete
    #@ ensures \result == n
    #@ assigns \nothing
    def name_of(self, n: str) -> str:
        return n

    #@ ensures \result[0] == n
    #@ assigns \nothing
    def variant(self, n: str, k: int) -> Tuple[str, List[str]]:
        c = self.name_of(n)
        types: List[str] = []
        if k > 0:
            types.append("int")
        return (c, types)


if __name__ == "__main__":
    r = B().variant("c", 1)
    print("VIOLATION contract" if r[0] != "c" else "result", r)
