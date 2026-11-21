r"""Test 5030 -- gen #37 route #371 (expected FAIL): frozen `D` with a field `z: Z`, `Z(N, M)` unhashable (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

class M:
    __hash__ = None

class N:
    pass

class Z(N, M):
    pass

@dataclass(frozen=True)
class D:
    z: Z

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(Z())))
