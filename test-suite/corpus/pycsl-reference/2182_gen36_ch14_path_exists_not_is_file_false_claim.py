r"""Test 2182 — ch14 seam (expected FAIL): `exists()` does NOT imply `is_file()` (a directory
exists and is not a file). CPython: `dir_is_file(Path("/"))` is 0 (`/tmp` exists, is a
directory). The two predicates are independent law-free `val`s, so the claim must stay
unproved. Control: 2180.
"""
# pycsl-expected: FAIL
from pathlib import Path


#@ ensures \result == 1
#@ assigns \nothing
def dir_is_file(d: Path) -> int:
    if (d / "tmp").exists():
        if (d / "tmp").is_file():
            return 1
        return 0
    return 1
