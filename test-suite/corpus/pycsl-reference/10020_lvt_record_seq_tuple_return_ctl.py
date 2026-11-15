r"""Test 10020 -- lvT record-list tuple return CONTROL (expected PASS): a verified
`-> Tuple[List[R], str]` function (R a record class of this file) returns the `seq r` its
`.append(R(..))` accumulator builds in the `List[R]` slot, as-is (no bridge, nothing erased), and
the `str` slot is exact. Twins (must FAIL): 10021, 10022.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List, Tuple


class Tk:
    def __init__(self, kind: str, start: int):
        self.kind: str = kind
        self.start: int = start


#@ ensures \result[1] == s + "!"
#@ assigns \nothing
def lex(s: str) -> Tuple[List[Tk], str]:
    toks = []
    toks.append(Tk("A", 0))
    toks.append(Tk("EOF", len(s)))
    return toks, s + "!"


if __name__ == "__main__":
    for s in ["", "ab"]:
        t, r = lex(s)
        print("VIOLATION contract" if r != s + "!" else "result", len(t), r)
