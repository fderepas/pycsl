r"""Test 10203 -- route #614 (expected FAIL): membership of a Path in a list of its own `str` (rt65
b03): CPython `Path("a") in ["a"]` is False (list membership is `==`); PROVED `\result == True` at
4d753c2f1. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return p in [str(p)]


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
