r"""Test 10242 -- route #617 (expected FAIL): ORDERING of two alias-annotated Paths (red team rt67
n18, PRE-EXISTING): `p < q` was decided as STRING order (`str_lt_op`), so with `str(p) == "a/b"`
and `str(q) == "a-b"` the claim `\result == False` PROVED; CPython orders Paths by parts and
`Path("a/b") < Path("a-b")` is True. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path


#@ requires str(p) == "a/b"
#@ requires str(q) == "a-b"
#@ ensures \result == False
#@ assigns \nothing
def f(p: Fp, q: Fp) -> bool:
    return p < q


if __name__ == "__main__":
    r = f(Path("a/b"), Path("a-b"))
    print("VIOLATION contract" if r is not False else "result", r)
