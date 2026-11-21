r"""Test 5448 -- gen #37 systematic rule S1 (expected FAIL): driver probe a1 -- `from collections import *` then `class D(UserList)`: the base is bound by a STANDARD-LIBRARY star import, which the first S1 cut did not resolve; `{d}` under `no_exception` PROVED at base 7bf752d4e and at 3e69a82b8 (CPython TypeError). REFUSED (PYCSL-S1-UNMODELLED-BASE: a name a stdlib star import may bind).
"""
# pycsl-expected: FAIL
from collections import *

class D(UserList):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
