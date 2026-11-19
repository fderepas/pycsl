r"""Test 10288 -- lvZ2 restricted Path type separation (expected PASS): two LOCALS built by the
modelled `Path(<str>)` from the same `str` are equal (`path_eq_op`, the equality of the abstract
`py_path` values; the constructor is deterministic). CPython: always True.
"""
# pycsl-expected: PASS
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    q = Path(s)
    return p == q


if __name__ == "__main__":
    r = f("a//b/")
    print("VIOLATION contract" if r is not True else "result", r)
