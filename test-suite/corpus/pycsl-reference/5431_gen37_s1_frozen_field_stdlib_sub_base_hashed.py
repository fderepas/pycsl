r"""Test 5431 -- gen #37 systematic rule S1 / route #381 (expected FAIL): red team 29 `h49_frozen_field_stdlib_sub` -- `class U(UserDict)` (a standard-library base the model has no entry for) hashed under `no_exception`; PROVED at base 7bf752d4e (CPython TypeError). REFUSED (PYCSL-S1-UNMODELLED-BASE).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from collections import UserDict

class U(UserDict):
    pass

@dataclass(frozen=True)
class D:
    u: U

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(U())))
