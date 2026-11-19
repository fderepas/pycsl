r"""Test 9101 -- lvI record-aware location stamp (expected FAIL): false twin of 9100. The record store `p.lineno = a + 2`
on a record-typed local must NOT be elided by the location-stamp gate: claiming the constructor argument
survives (`\result == a`) must not prove. CPython: `restamp(5)` is 7.
"""
# pycsl-expected: FAIL
from __future__ import annotations


class Pos:
    def __init__(self, lineno: int, col_offset: int):
        self.lineno = lineno
        self.col_offset = col_offset


class Box:
    def __init__(self, k: int):
        self.k = k


class _Parser:
    def __init__(self, depth: int):
        self.depth = depth

    #@ ensures \result == n
    #@ assigns \nothing
    def _fin(self, n: int) -> int:
        return n


#@ assigns node
def stamp(node):
    node.lineno = 3
    node.col_offset = 4


#@ ensures \result == a
#@ assigns \nothing
def restamp(a: int) -> int:
    p = Pos(a, 0)
    p.lineno = a + 2
    return p.lineno


if __name__ == "__main__":
    b = Box(1)
    stamp(b)
    r = restamp(5)
    print("result", r, b.lineno)
