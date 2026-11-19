r"""Test 5143 -- gen #37 route #378 (expected FAIL): `n: int = field(default=3, init=False)` then `n = -1`: the goal read default 3; dataclasses reads the class `__dict__` after the body ran (CPython -1). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

#@ class invariant self.n >= 0
@dataclass
class D:
    x: int
    n: int = field(default=3, init=False)
    n = -1

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.n

if __name__ == "__main__":
    print(f(D(1)))
