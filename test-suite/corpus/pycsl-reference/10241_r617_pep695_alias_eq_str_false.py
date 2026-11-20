r"""Test 10241 -- route #617 (expected FAIL): the PEP 695 alias `type Fp = Path` (red team rt67
n24, PRE-EXISTING): `p == str(p)` on an `Fp` parameter PROVED `\result == True`; CPython False.
REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path

type Fp = Path


#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    r = f(Path("a"))
    print("VIOLATION contract" if r is not True else "result", r)
