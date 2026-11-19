r"""Test 10253 -- route #617 (expected FAIL): MEMBERSHIP of an alias-annotated Path in a list of
its own `str` (red team rt67 n29, PRE-EXISTING: lowered to `str_eq_op p p`); CPython
`p in [str(p)]` is False. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path


#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    return p in [str(p)]


if __name__ == "__main__":
    r = f(Path("a"))
    print("VIOLATION contract" if r is not True else "result", r)
