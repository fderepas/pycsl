r"""Test 8606 -- route #542 (control, expected PASS): `in` a dict / str, `for` over a str / `range(k)` / a `List[int]`; CPython 1 2 3 3 1
"""
# pycsl-expected: PASS
from typing import Dict, List


#@ no_exception \all
def f(k: int, d: Dict[str, int]) -> int:
    if "k" in d:
        return 1
    return 0


#@ no_exception \all
def g(k: int, s: str) -> int:
    n = 0
    for c in s:
        n += 1
    return n


#@ no_exception \all
def h(k: int) -> int:
    n = 0
    for i in range(k):
        n += 1
    return n


#@ no_exception \all
def u(k: int, xs: List[int]) -> int:
    n = 0
    for x in xs:
        n += x
    return n


#@ no_exception \all
def v(k: int, s: str) -> int:
    if "a" in s:
        return 1
    return 0


if __name__ == "__main__":
    print(f(0, {"k": 1}), g(0, "ab"), h(3), u(0, [1, 2]), v(0, "abc"))
