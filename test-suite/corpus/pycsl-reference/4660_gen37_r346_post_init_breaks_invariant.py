r"""Test 4660 -- gen #37 route #346 (expected FAIL): witness k08: `@dataclass` + `#@ class invariant self.x >= 0`, `__post_init__` stores -1; no constructor goal, invariant assumed; PROVED (CPython -1). REFUSED (PYCSL-R346-POST-INIT-INVARIANT, route #346).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    def __post_init__(self) -> None:
        self.x = -1

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(3)) >= 0
