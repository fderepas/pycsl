r"""Test 10201 -- route #614 (expected FAIL): a `p: Path` PARAMETER compared with `str(p)` (rt65
a07, PRE-EXISTING through #31's annotation erasure: PROVED at 0057c8b94 and at 4d753c2f1); CPython
`p == str(p)` is False for every Path. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(p: Path) -> bool:
    return p == str(p)


if __name__ == "__main__":
    r = f(Path("a"))
    print("VIOLATION contract" if r is not True else "result", r)
