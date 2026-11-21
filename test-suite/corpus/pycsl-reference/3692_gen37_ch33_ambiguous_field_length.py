r"""Test 3692 -- gen #37 ch33 (expected PASS): `\length(self.toks)` on a field name SHARED by two classes (so declared under the qualified label `p_toks`): the class-invariant and method-contract arms of `_handle_arraylen_expr` printed the RAW name (`Array.length toks` / `self.toks`), `unbound function or predicate symbol 'toks'`. Now labelled as `_handle_field_get_expr` does. Honest claim must PROVE.
"""
from typing import List


#@ class invariant \length(self.toks) >= 0
class P:
    def __init__(self) -> None:
        self.toks: List[int] = [1, 2, 3]
        self.i: int = 0

    #@ requires \length(self.toks) >= 1
    #@ ensures \result == self.toks[0]
    #@ assigns \nothing
    def first(self) -> int:
        return self.toks[0]


class Q:
    def __init__(self) -> None:
        self.toks: List[int] = [7]
