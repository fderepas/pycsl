r"""Test 6026 -- gen #37 route #409 (expected PASS): CONTROL: hashable standard-library objects (`os.sep`, `os.getcwd`, `os.path`) hashed (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
import math
import os


#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    s = {os.sep, os.getcwd, os.path}
    return 1


if __name__ == "__main__":
    print(f())
