r"""Test 8605 -- route #541 (control, expected PASS): a str list taking str values (an f-string display, `.append("c")`), a `List[Optional[str]]` taking None and tested before use, a `List[int]` taking ints; CPython 2 1 2
"""
# pycsl-expected: PASS
from typing import List, Optional


#@ no_exception \all
def f(k: int) -> int:
    a: List[str] = [f"ab"]
    a.append("c")
    return len(a)


#@ no_exception \all
def g(k: int) -> int:
    a: List[Optional[str]] = []
    a.append(None)
    a.append("x")
    n = 0
    for p in a:
        if p is not None:
            n += 1
    return n


#@ no_exception \all
def h(k: int) -> int:
    xs: List[int] = []
    xs.append(k)
    xs.append(len("ab"))
    return len(xs)


if __name__ == "__main__":
    print(f(0), g(0), h(3))
