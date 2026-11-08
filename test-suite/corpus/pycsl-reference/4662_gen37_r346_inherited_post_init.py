r"""Test 4662 -- gen #37 route #346 (expected FAIL): (new) `B(A)` with the invariant on B, `A.__post_init__` stores -1; PROVED (CPython -1). REFUSED (PYCSL-R346-POST-INIT-INVARIANT, route #346).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class A:
    x: int
    def __post_init__(self) -> None:
        self.x = -1

#@ class invariant self.x >= 0
@dataclass
class B(A):
    y: int = 0

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B(3)) >= 0
