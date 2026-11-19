r"""Test 10248 -- route #617 (expected FAIL): a `Path(<str>)` passed through the IMPORTED
`ident(p: Path) -> Path` (red team rt67 m02, INTRODUCED by batch C: PROVED at ff01853ec, refused at
899b6869d); `q == str(q)` is False in CPython. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from multi_file_lib.r617_pathlib import ident


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = ident(Path(s))
    return q == str(q)


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
