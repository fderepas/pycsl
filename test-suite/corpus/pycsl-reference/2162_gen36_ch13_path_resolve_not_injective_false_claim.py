r"""Test 2162 — ch13 seam S-c (expected FAIL): `Path.resolve()` is NOT injective. CPython:
`Path("a/../b").resolve() == Path("b").resolve()` although the two paths differ, so
`p != q -> p.resolve() != q.resolve()` is false. `path_resolve_op` is an impure, law-free `val`,
so the claim must stay unproved. Control: 2160.
"""
# pycsl-expected: FAIL
from pathlib import Path


#@ requires p != q
#@ ensures \result == 1
#@ assigns \nothing
def differ(p: Path, q: Path) -> int:
    if p.resolve() != q.resolve():
        return 1
    return 0
