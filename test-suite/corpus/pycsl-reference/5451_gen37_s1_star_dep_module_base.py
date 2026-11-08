r"""Test 5451 -- gen #37 systematic rule S1 (expected FAIL): driver probe b1 -- the imported module star-imports collections (`from collections import *; class D(UserList)` in the dependency); `{d}` under `no_exception` PROVED at base 7bf752d4e (CPython TypeError). REFUSED (PYCSL-S1-UNMODELLED-BASE in the imported module).
"""
# pycsl-expected: FAIL
from multi_file_lib.s1_star_dep import D

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
