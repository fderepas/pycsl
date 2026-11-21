r"""Test 5045 -- gen #37 route #372 (expected FAIL): NEW shape: `{r.e.d}`, a field of a field stored from typed parameters (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

class E:
    def __init__(self, d: D) -> None:
        self.d = d

class R:
    def __init__(self, e: E) -> None:
        self.e = e

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r.e.d}
    return 1

if __name__ == "__main__":
    print(g(R(E(D(1)))))
