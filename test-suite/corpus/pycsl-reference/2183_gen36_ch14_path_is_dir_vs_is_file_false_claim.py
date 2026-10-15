r"""Test 2183 — ch14 seam (expected FAIL): `is_dir()` and `is_file()` are different predicates.
CPython: `same_kind(Path("/"))` is 0 (`/tmp` is a directory, not a file). The model must not
identify the two ops, so `\result == 1` must stay unproved. Control: 2180.
"""
# pycsl-expected: FAIL
from pathlib import Path


#@ ensures \result == 1
#@ assigns \nothing
def same_kind(d: Path) -> int:
    if (d / "tmp").is_dir() == (d / "tmp").is_file():
        return 1
    return 0
