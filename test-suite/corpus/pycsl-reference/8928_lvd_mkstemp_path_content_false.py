r"""Test 8928 -- lvD `tempfile.mkstemp` pair (expected FAIL): false twin of 8926. The model carries no
content law, so `\result == ""` must NOT prove (CPython: an absolute, non-empty path).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import os
import tempfile


#@ ensures \result == ""
#@ assigns \nothing
def make_path() -> str:
    fd, path = tempfile.mkstemp()
    os.close(fd)
    return path


if __name__ == "__main__":
    p = make_path()
    print("VIOLATION contract" if p != "" else "result", p)
    os.unlink(p)
