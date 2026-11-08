r"""Test 8927 -- lvD `tempfile.mkstemp` pair (expected FAIL): false twin of 8926. Each call creates a
NEW file, so two calls return different paths; the model is a plain `val` (no determinism law), so
`\result == True` (equal paths) must NOT prove (CPython: False).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import os
import tempfile


def make_path() -> str:
    fd, path = tempfile.mkstemp(suffix=".x")
    os.close(fd)
    return path


#@ ensures \result == True
#@ assigns \nothing
def same_path() -> bool:
    a = make_path()
    b = make_path()
    return a == b


if __name__ == "__main__":
    r = same_path()
    print("VIOLATION contract" if r is not True else "result", r)
