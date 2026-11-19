r"""Test 10243 -- route #617 (expected FAIL): `!=` between an alias-annotated Path and its `str` in
a branch (red team rt67 n17, PRE-EXISTING): `t = str(p); if p != t: return 0` PROVED
`\result == 1`; CPython returns 0 (a Path never equals a str). REFUSED
(`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path


#@ ensures \result == 1
#@ assigns \nothing
def f(p: Fp) -> int:
    t = str(p)
    if p != t:
        return 0
    return 1


if __name__ == "__main__":
    r = f(Path("a"))
    print("VIOLATION contract" if r != 1 else "result", r)
