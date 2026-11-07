r"""Test 5450 -- gen #37 systematic rule S1 (expected FAIL): driver probe a11 -- `from multi_file_lib.s1_userlist_base import D as E; D = E`, the imported `class D(UserList)` re-bound under its own name; `{d}` under `no_exception` PROVED at base 7bf752d4e and at 3e69a82b8 (CPython TypeError). REFUSED (PYCSL-S1-UNMODELLED-BASE in the imported module).
"""
# pycsl-expected: FAIL
from multi_file_lib.s1_userlist_base import D as E
D = E

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
