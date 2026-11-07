r"""Test 5034 -- gen #37 route #372 (expected FAIL): `{self.d}` in a method (CPython raises / violates; PROVED at base dc378283).
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
    def g(self) -> int:
        s = {self.d}
        return 1

if __name__ == "__main__":
    print(R(D(1)).g())
