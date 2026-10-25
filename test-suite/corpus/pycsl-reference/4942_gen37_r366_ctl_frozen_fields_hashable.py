r"""Test 4942 -- gen #37 route #366 (expected PASS): CONTROL: frozen record with int / Optional[float] / forward-ref NamedTuple / Tuple[int, ...] / FrozenSet fields and an unsafe_hash record with an int field are hashable (CPython ok).
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import NamedTuple, Optional, Tuple, FrozenSet

class P(NamedTuple):
    a: int
    b: str

@dataclass(frozen=True)
class D:
    x: int
    y: Optional[float]
    p: "P"
    t: Tuple[int, ...]
    fs: FrozenSet[int]

@dataclass(unsafe_hash=True)
class U:
    n: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D, u: U) -> int:
    s = {d}
    t = {u}
    return 1

if __name__ == "__main__":
    print(g(D(1, None, P(1, "a"), (1, 2), frozenset({1})), U(3)))
