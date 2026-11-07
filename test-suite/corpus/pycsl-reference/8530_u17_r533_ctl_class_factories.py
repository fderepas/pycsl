r"""Test 8530 -- route #533 (control, expected PASS): program classes called as a dataclass `default_factory` with no argument -- an `__init__` whose parameters all have defaults, a class inheriting it, a dataclass whose fields all have defaults (one a nested class factory), a class with no `__init__`; none raises; CPython f(5) returns 5
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import Any


class Q:
    def __init__(self, k: int = 0) -> None:
        self.k = k


class R(Q):
    pass


class E:
    pass


@dataclass
class D:
    m: int = 0
    q: Any = field(default_factory=Q)


@dataclass
class P:
    a: int
    b: Any = field(default_factory=Q)
    c: Any = field(default_factory=R)
    d: Any = field(default_factory=D)
    e: Any = field(default_factory=E)


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    p = P(n)
    return p.a


if __name__ == "__main__":
    print(f(5))
