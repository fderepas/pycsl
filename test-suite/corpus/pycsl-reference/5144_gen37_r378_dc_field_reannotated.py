r"""Test 5144 -- gen #37 route #378 (expected FAIL): a dataclass field annotated twice: the first `field(default=3)` was read (CPython -1). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

#@ class invariant self.n >= 0
@dataclass
class D:
    x: int
    n: int = field(default=3, init=False)
    n: int = field(default=-1, init=False)

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.n

if __name__ == "__main__":
    print(f(D(1)))
