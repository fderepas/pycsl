r"""Test 8892 -- route #562 (control, expected PASS): comprehensions over a `List[int]` read a record field (`p.a + x`), call its method with an int (`p.m(x)`), construct it with an int (`P(x).a`) and search the list (`p.a in xs`); CPython 2 1 1 2 1
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import List


@dataclass
class P:
    a: int

    def m(self, y: int) -> int:
        return self.a + y


#@ no_exception \all
def f1(xs: List[int], p: P) -> int:
    return len([p.a + x for x in xs])


#@ no_exception \all
def f2(xs: List[int], p: P) -> int:
    return len([p.m(x) for x in xs])


#@ no_exception \all
def f3(xs: List[int]) -> int:
    return len([P(x).a for x in xs])


#@ no_exception \all
def f4(xs: List[int], p: P) -> int:
    return sum(p.a for x in xs)


#@ no_exception \all
def f5(xs: List[int], p: P) -> int:
    return len([p.a in xs for x in xs])


if __name__ == "__main__":
    print(f1([1, 2], P(1)), f2([1], P(1)), f3([1]), f4([1], P(2)), f5([1], P(1)))
