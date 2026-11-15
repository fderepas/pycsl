r"""Test 10022 -- lvT record-list tuple return (expected FAIL): the `List[Tk]` slot is filled with
a list of `str`, not of `Tk` records (CPython would return it, but the declared slot type is false
of it); the slot is the declared `seq tk`, so a `seq string` value there is a Why3 type error
(fail-closed, never an int-erased pass). Control: 10020.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List, Tuple


class Tk:
    def __init__(self, kind: str, start: int):
        self.kind: str = kind
        self.start: int = start


#@ requires True
#@ ensures \result[1] == s
#@ assigns \nothing
def lex(s: str) -> Tuple[List[Tk], str]:
    toks = []
    toks.append("A")
    return toks, s


if __name__ == "__main__":
    t, r = lex("a")
    print("VIOLATION type" if not all(isinstance(x, Tk) for x in t) else "result", t)
