r"""Test 5449 -- gen #37 systematic rule S1 (expected FAIL): driver probe a4 -- `from multi_file_lib.s1_userlist_base import D`, whose module defines `class D(UserList)` and never names it: the first S1 cut checked only the main file's referenced classes; `{d}` under `no_exception` PROVED at base 7bf752d4e and at 3e69a82b8 (CPython TypeError). REFUSED (PYCSL-S1-UNMODELLED-BASE in the imported module: every class of a dependency is checked).
"""
# pycsl-expected: FAIL
from multi_file_lib.s1_userlist_base import D

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
