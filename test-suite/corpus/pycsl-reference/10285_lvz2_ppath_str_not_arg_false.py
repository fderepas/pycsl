r"""Test 10285 -- lvZ2 restricted Path type separation (expected FAIL): `str(p)` of a modelled
`p = Path(s)` is the law-free `path_str_op` (no inverse, no relation to `s`): CPython
normalises `Path("a//b")` to `a/b`, so `str(p) == s` is not derivable.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return str(p) == s


if __name__ == "__main__":
    r = f("a//b")
    print("VIOLATION contract" if r is not True else "result", r)
