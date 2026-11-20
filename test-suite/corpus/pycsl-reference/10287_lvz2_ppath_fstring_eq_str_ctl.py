r"""Test 10287 -- lvZ2 restricted Path type separation (expected PASS): `f"{p}"` of a modelled
`p = Path(s)` is `str(p)` (`path_str_op p`), as in CPython.
"""
# pycsl-expected: PASS
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return f"{p}" == str(p)


if __name__ == "__main__":
    r = f("a//b/")
    print("VIOLATION contract" if r is not True else "result", r)
