r"""Test 8890 -- route #561 (control, expected PASS): generator expressions consumed by `sum` / `any` / `all` / `max(.., default=0)` / `tuple` iterate a `List[int]`, a `range(k)`, a `str` and a `Dict[str, int]` -- never a record or a function; CPython 2 3 2 1 True True 2 1
"""
# pycsl-expected: PASS
from typing import Dict, List


#@ no_exception \all
def f1(xs: List[int]) -> int:
    return sum(1 for x in xs)


#@ no_exception \all
def f2(k: int) -> int:
    return sum(1 for x in range(k))


#@ no_exception \all
def f3(s: str) -> int:
    return sum(1 for c in s)


#@ no_exception \all
def f4(d: Dict[str, int]) -> int:
    return sum(1 for kk in d)


#@ no_exception \all
def f5(xs: List[int]) -> bool:
    return any(x > 0 for x in xs)


#@ no_exception \all
def f6(xs: List[int]) -> bool:
    return all(x > 0 for x in xs)


#@ no_exception \all
def f7(xs: List[int]) -> int:
    return max((x for x in xs), default=0)


#@ no_exception \all
def f8(xs: List[int]) -> int:
    return len(tuple(x for x in xs))


if __name__ == "__main__":
    print(f1([1, 2]), f2(3), f3("ab"), f4({"a": 1}), f5([1]), f6([1]), f7([1, 2]), f8([1]))
