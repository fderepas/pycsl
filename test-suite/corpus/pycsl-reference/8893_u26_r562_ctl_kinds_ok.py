r"""Test 8893 -- route #562 (control, expected PASS): comprehension elements apply unary `-` / `~` to ints, test a str needle in a str, order strs and concatenate strs; CPython 1 1 1 1 1
"""
# pycsl-expected: PASS
from typing import List


def h(x: int) -> int:
    return x + 1


#@ no_exception \all
def f1(xs: List[int]) -> int:
    return len([-x for x in xs])


#@ no_exception \all
def f2(xs: List[int]) -> int:
    return len([~x for x in xs])


#@ no_exception \all
def f3(ss: List[str], t: str) -> int:
    return len([s in t for s in ss])


#@ no_exception \all
def f4(ss: List[str], t: str) -> int:
    return len([s < t for s in ss])


#@ no_exception \all
def f6(ss: List[str], t: str) -> int:
    return len({s + t for s in ss})


if __name__ == "__main__":
    print(f1([1]), f2([1]), f3(["a"], "ab"), f4(["a"], "b"), f6(["a"], "b"))
