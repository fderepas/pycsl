r"""Test 10142 -- lvX `Path(<str>)` model (expected FAIL): `Path("")` is `.` in CPython, so
`str(Path("")) == ""` is False and `\result == True` must NOT prove (no identity law, no
length law).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def empty_kept() -> bool:
    return str(Path("")) == ""


if __name__ == "__main__":
    r = empty_kept()
    print("VIOLATION contract" if r is not True else "result", r)
