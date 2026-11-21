r"""Test 10206 -- route #614 (expected FAIL): `f"{p}" == p` (rt65 b09): the f-string of a Path IS a
`str`, which CPython never equates with the Path; the model lowered both to the same string and
PROVED `\result == True` at 4d753c2f1. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return f"{p}" == p


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
