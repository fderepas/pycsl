r"""Test 10286 -- lvZ2 restricted Path type separation (expected PASS): `os.fspath(p)` and
`str(p)` of a modelled `p = Path(s)` are the SAME law-free `path_str_op p` (CPython: both are
the path's string), so their equality holds.
"""
# pycsl-expected: PASS
from __future__ import annotations
import os
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return os.fspath(p) == str(p)


if __name__ == "__main__":
    r = f("a//b/")
    print("VIOLATION contract" if r is not True else "result", r)
