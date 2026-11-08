r"""Test 5338 -- gen #37 route #381 (expected FAIL): `class D(argparse.Namespace)`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from argparse import Namespace

class D(Namespace):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
