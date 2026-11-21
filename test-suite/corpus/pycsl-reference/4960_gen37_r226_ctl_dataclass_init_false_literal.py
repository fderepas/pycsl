r"""Test 4960 -- gen #37 route #226: CONTROL: a mixed-field `@dataclass` (`s: str`, `n: int = field(default=3, init=False)`) whose invariant `self.n >= 0` holds for EVERY constructor input (`n` is not an `__init__` parameter); the projection states `forall n. n = 3 -> n >= 0` and the file PROVES (CPython 3).
"""
from dataclasses import dataclass, field

#@ class invariant self.n >= 0
@dataclass
class D:
    s: str
    n: int = field(default=3, init=False)

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.n

if __name__ == "__main__":
    assert f(D("a")) == 3
