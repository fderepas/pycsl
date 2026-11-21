r"""Test 9141 -- lvD3 (rt54 R54-F4 fc1529, expected FAIL): `name = ""; if name:` -- CPython takes the
false branch (returns 0). C2 made `name` the nonzero hash of "" so `\result == 1` proved. A truthiness read
is not an opaque position: C2 does not fire.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 1
#@ assigns \nothing
def f(x) -> int:
    name = x
    name = ""
    if name:
        return 1
    return 0


if __name__ == "__main__":
    r = f(3)
    print("VIOLATION contract" if r != 1 else "result", r)
