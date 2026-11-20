r"""Test 10284 -- lvZ2 restricted Path type separation (expected FAIL): `.exists()` of a modelled
`Path(<str>)` is the IMPURE, law-free `ppath_exists_op` (a `py_path` receiver): nothing is
claimed about the filesystem, so `\result == True` is not derivable (CPython: False for a
missing path).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return p.exists()


if __name__ == "__main__":
    r = f("/nonexistent-lvz2/x")
    print("VIOLATION contract" if r is not True else "result", r)
