r"""Test 8891 -- route #562 (control, expected PASS): comprehension / generator elements call file functions with arguments of the declared kinds (`h(x)` of `x` in a `List[int]`, `hs(s)` of `s` in a `List[str]`), with filters, two `for` clauses and a nested comprehension; CPython 2 1 1 1 5 2
"""
# pycsl-expected: PASS
from typing import List


def h(x: int) -> int:
    return x + 1


def hs(x: str) -> int:
    return len(x + "c")


#@ no_exception \all
def f1(xs: List[int]) -> int:
    return len([h(x) for x in xs])


#@ no_exception \all
def f2(ss: List[str], t: str) -> int:
    return len([hs(s) for s in ss if s != t])


#@ no_exception \all
def f3(xs: List[int]) -> int:
    return len([[y for y in xs] for x in xs])


#@ no_exception \all
def f4(xs: List[int]) -> int:
    return len([x + y for x in xs for y in xs if x < y])


#@ no_exception \all
def f5(k: int, xs: List[int]) -> int:
    return sum(h(x) for x in xs if x > k)


#@ no_exception \all
def f6(ss: List[str]) -> int:
    return sum(hs(s) for s in ss)


if __name__ == "__main__":
    print(f1([1, 2]), f2(["a", "b"], "a"), f3([1]), f4([1, 2]), f5(0, [1, 2]), f6(["a"]))
