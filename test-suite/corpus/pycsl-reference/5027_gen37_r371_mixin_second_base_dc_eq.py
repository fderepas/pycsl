r"""Test 5027 -- gen #37 route #371 (expected FAIL): `D(N, M)` with an eq-`@dataclass` `M` (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class M:
    y: int = 0

class N:
    pass

class D(N, M):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D()))
