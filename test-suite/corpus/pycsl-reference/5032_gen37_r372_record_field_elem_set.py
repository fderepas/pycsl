r"""Test 5032 -- gen #37 route #372 (expected FAIL): `{r.d}`, `self.d = d` stored from a typed parameter (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

class R:
    def __init__(self, d: D) -> None:
        self.d = d

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r.d}
    return 1

if __name__ == "__main__":
    print(g(R(D(1))))
