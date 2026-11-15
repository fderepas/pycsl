r"""Test 10021 -- lvT record-list tuple return (expected FAIL): the `str` slot of the returned
tuple is `s + "!"`, so the claim `\result[1] == s` is false (CPython: `lex("a")[1]` is "a!").
Control: 10020.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List, Tuple


class Tk:
    def __init__(self, kind: str, start: int):
        self.kind: str = kind
        self.start: int = start


#@ ensures \result[1] == s
#@ assigns \nothing
def lex(s: str) -> Tuple[List[Tk], str]:
    toks = []
    toks.append(Tk("A", 0))
    return toks, s + "!"


if __name__ == "__main__":
    t, r = lex("a")
    print("VIOLATION contract" if r != "a" else "result", r)
