r"""Test 2181 — ch14 seam (expected FAIL): `Path.is_file()` is not always true. CPython:
`present(Path("/nonexistent-pycsl-dir"))` is 0. `path_isfile_op` is an impure, law-free `val`,
so `\result == 1` must stay unproved. Control: 2180.
"""
# pycsl-expected: FAIL
from pathlib import Path


#@ ensures \result == 1
#@ assigns \nothing
def present(d: Path) -> int:
    if (d / "f").is_file():
        return 1
    return 0
