r"""Test 8815 -- route #556 (control, expected PASS): builtin functions are CALLED (`len`, `abs`, `range`), never searched or iterated; `in` / `for` run over a dict, a str, a `range(..)` and a `List[int]`; CPython 1 1 3 3 2
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
    if "a" in s:
        return 1
    return 0


#@ no_exception \all
def h(k: int) -> int:
    n = 0
    for i in range(abs(k)):
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
    return len(s)


if __name__ == "__main__":
    print(f(0, {"k": 1}), g(0, "abc"), h(-3), u(0, [1, 2]), v(0, "ab"))
