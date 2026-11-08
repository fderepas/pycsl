r"""Test 8926 -- lvD `tempfile.mkstemp` pair (expected PASS): `fd, path = tempfile.mkstemp(..)` is an
`(int, str)` pair in CPython, so the path target is let-bound from the `(int, string)` slot of the plain
(non-deterministic, law-free) `val tempfile_mkstemp_0 () : (int, string)`, and `path + ""` compares
equal to it as a string. At base both slots were `int` and the body was a Why3 type error. Twins: 8927,
8928 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import os
import tempfile


#@ ensures \result == True
#@ assigns \nothing
def path_copy_equal() -> bool:
    fd, path = tempfile.mkstemp(prefix=".w_", suffix=".mlw")
    os.close(fd)
    return path + "" == path


if __name__ == "__main__":
    r = path_copy_equal()
    print("VIOLATION contract" if r is not True else "result", r)
