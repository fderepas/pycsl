r"""Test 5384 -- gen #37 route #383 (expected FAIL): NEW shape: `e: B`, `{e.d}` with field `d: D` defined only by subclass `S(B)` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

class B:
    def __init__(self) -> None:
        self.n = 1

class S(B):
    def __init__(self, d: D) -> None:
        self.n = 1
        self.d = d

#@ no_exception \all
#@ ensures \result == 1
def g(e: B) -> int:
    if isinstance(e, S):
        s = {e.d}
    return 1

if __name__ == "__main__":
    print(g(S(D(1))))
