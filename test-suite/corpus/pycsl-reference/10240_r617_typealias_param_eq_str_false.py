r"""Test 10240 -- route #617 (expected FAIL): a parameter annotated through a `TypeAlias` of Path
(`Fp: TypeAlias = Path`) compared with `str(p)` (red team rt67 n02, PRE-EXISTING: #31 resolves the
alias and erases the parameter to `string`, so `p == str(p)` was `str_eq_op p p` and PROVED);
CPython `p == str(p)` is False for every Path. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`: the R614
annotation test now resolves Path aliases).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path


#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    r = f(Path("a"))
    print("VIOLATION contract" if r is not True else "result", r)
