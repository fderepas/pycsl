r"""Test 3356 -- route #293 (expected FAIL): red-team os001: `r1 = os.path.relpath("a", "/"); os.chdir("/tmp"); r2 = ...; check r1 == r2` PROVED (`relpath` was a `val function`); CPython resolves the relative path against the cwd.
Now `relpath` is an impure `val`; the check is unproven.
"""
# pycsl-expected: FAIL
import os


#@ ensures \result == 1
def f() -> int:
    r1 = os.path.relpath("a", "/")
    os.chdir("/tmp")
    r2 = os.path.relpath("a", "/")
    #@ check r1 == r2
    return 1


if __name__ == "__main__":
    os.chdir("/")
    r1 = os.path.relpath("a", "/")
    os.chdir("/tmp")
    r2 = os.path.relpath("a", "/")
    assert r1 != r2, (r1, r2)
