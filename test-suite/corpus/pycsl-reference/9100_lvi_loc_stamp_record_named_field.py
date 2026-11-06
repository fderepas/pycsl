r"""Test 9100 -- lvI record-aware location stamp (expected PASS). The pure_ast parser gate (`_uses_pyast_parser`: the
file defines `_Parser._fin`) lowers a location stamp `node.lineno = ..` on a NON-record object to its
non-record form; the field-store arm tested `field in self._all_record_fields`, a NAME test, so once a
user record (`Pos`) declares `lineno` the stamp on the untyped `node` became the record store
`node.lineno <- 3` on an `int` and the file did not type-check (base: L3-tc fails). A store on a
RECORD-typed local keeps the record store: `p.lineno = a + 2` is read back. Twins 9101 / 9102 (FAIL).
"""
# pycsl-expected: PASS
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


#@ ensures \result == a + 2
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
