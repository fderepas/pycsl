r"""Test 9177 -- routes #569 / #570 (control, expected PASS): `for` / `in` over real containers -- a `List[int]` and a `str` iterated, a module str (`os.sep`) searched for a str needle and iterated, a tuple display searched for an int; generators / nested comprehensions over a CALLED str / dict method (`s.upper()`, `d.keys()`), a str and a list -- never a class object, `...`, `__builtins__` or a bound method; CPython 2 1 1 1 2 2 1 4 2
"""
# pycsl-expected: PASS
from typing import Dict, List
import os


#@ no_exception \all
def f2(xs: List[int]) -> int:
    t = 0
    for x in xs:
        t += 1
    return t


#@ no_exception \all
def f3(k: int) -> int:
    return 1 if "/" in os.sep else 0


#@ no_exception \all
def f4(s: str) -> int:
    return 1 if s in os.sep else 0


#@ no_exception \all
def f5(k: int) -> int:
    return 1 if k in (1, 2) else 0


#@ no_exception \all
def f6(s: str) -> int:
    t = 0
    for c in s:
        t += 1
    return t


#@ no_exception \all
def g1(s: str) -> int:
    return sum(1 for c in s.upper())


#@ no_exception \all
def g2(d: Dict[str, int]) -> int:
    return sum(1 for kk in d.keys())


#@ no_exception \all
def g3(xs: List[int], s: str) -> int:
    return len([y for x in xs for y in s])


#@ no_exception \all
def g4(xs: List[int], ys: List[int]) -> int:
    return len([y for x in xs for y in ys])


if __name__ == "__main__":
    print(f2([1, 2]), f3(1), f4("/"), f5(2), f6("ab"), g1("ab"), g2({"a": 1}), g3([1, 2], "ab"), g4([1], [2, 3]))
