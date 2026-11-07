r"""Test 5341 -- gen #37 route #381 (expected FAIL): frozen dataclass with a UserDict-subclass field, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
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
