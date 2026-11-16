r"""Test 10077 -- lvU `os.access` (expected FAIL): the model reads a `str` path; an int argument is
REFUSED (PYCSL-R7U-EXT-ACCESS-PATH) rather than lowered to the str query, whose raise set has no
TypeError. CPython: `can_run(3)` raises TypeError ("path should be string, bytes or
os.PathLike"), so `\result == 1` is never established. Control: 10070.
"""
# pycsl-expected: FAIL
import os


#@ ensures \result == 1
#@ assigns \nothing
def can_run(fd: int) -> int:
    if os.access(fd, os.X_OK):
        return 1
    return 0


if __name__ == "__main__":
    try:
        r = can_run(3)
        print("VIOLATION contract" if r != 1 else "result", r)
    except TypeError:
        print("VIOLATION TypeError")
