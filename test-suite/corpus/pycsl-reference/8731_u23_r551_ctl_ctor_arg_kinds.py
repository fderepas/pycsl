r"""Test 8731 -- route #551 (control, expected PASS): constructions whose arguments are of the declared parameter / field kinds: a str parameter, a str literal, a keyword argument, a list of ints, a dataclass int field from `len(..)`; CPython 1 2 3
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import List


class C:
    def __init__(self, s: str) -> None:
        self.n = len(s)


class S:
    def __init__(self, xs: List[int]) -> None:
        self.n = sum(xs)


@dataclass
class R:
    a: int


#@ no_exception \all
def f(k: int, s: str) -> int:
    c = C(s)
    e = C(s=s)
    q = C("ab")
    return 1


#@ no_exception \all
def g(k: int) -> int:
    t = S([1, k])
    return 2


#@ no_exception \all
def h(xs: List[int]) -> int:
    r = R(len(xs))
    return 3


if __name__ == "__main__":
    print(f(1, "ab"), g(1), h([1]))
