r"""Test 10207 -- route #614 (expected PASS): CONTROL, the advice of `PYCSL-R614-PATH-STR-CONFLATED`
followed: compare the STRINGS (`str(p)`), which are `str` values in CPython too. `q = str(p)` and
`q == str(p)` is True for every Path (str() of a Path is deterministic).
"""
# pycsl-expected: PASS
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(p: Path) -> bool:
    q = str(p)
    return q == str(p)


if __name__ == "__main__":
    r = f(Path("a//b"))
    print("VIOLATION contract" if r is not True else "result", r)
