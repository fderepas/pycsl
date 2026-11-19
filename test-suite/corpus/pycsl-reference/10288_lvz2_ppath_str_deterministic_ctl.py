r"""Test 10288 -- lvZ2 restricted Path type separation (expected PASS): `str(p)` of a modelled
`p = Path(s)` is the deterministic `val function path_str_op p`, so two renderings of the same
Path agree (CPython: always True).
"""
# pycsl-expected: PASS
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    t = str(p)
    return t == str(p)


if __name__ == "__main__":
    r = f("a//b/")
    print("VIOLATION contract" if r is not True else "result", r)
