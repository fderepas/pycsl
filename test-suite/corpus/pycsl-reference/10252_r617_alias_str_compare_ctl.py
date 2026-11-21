r"""Test 10252 -- route #617 (expected PASS): CONTROL -- the advice of the refusal followed on an
alias-annotated Path: compare the STRINGS (`str(p)`), which are `str` values in CPython too
(`q = str(p); q == str(p)` is True for every Path).
"""
# pycsl-expected: PASS
from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path


#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    q = str(p)
    return q == str(p)


if __name__ == "__main__":
    r = f(Path("a//b"))
    print("VIOLATION contract" if r is not True else "result", r)
