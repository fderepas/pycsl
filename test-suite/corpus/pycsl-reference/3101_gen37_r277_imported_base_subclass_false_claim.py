r"""Test 3101 — route #277 (expected FAIL): the base `A` and its caller `use(a: A)` live in an
imported module (verified alone they are fine); this unit subclasses `A` with `m == 2` and
claims `g(B()) == 1` through `use`. PROVED by default (CPython 2); the refinement goal of the
local override against the IMPORTED base is now emitted by default and fails.
"""
# pycsl-expected: FAIL
from multi_file_lib.r277_base import A, use


class B(A):
    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2


#@ ensures \result == 1
#@ assigns \nothing
def g(a: A) -> int:
    return use(a)


if __name__ == "__main__":
    print(g(B()))
    assert g(B()) == 2
