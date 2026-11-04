r"""Test 8732 -- route #552 (control, expected PASS): ranges and dict views used at their own kinds -- iterated, sized -- and numbers derived from them passed to int parameters (a file and an imported function) and compared; a list copy passed to an int-declared parameter the callee never uses as a number; CPython 3 1 2 0
"""
# pycsl-expected: PASS
from typing import Dict, List

from multi_file_lib.u23_dep552 import g as gi


def h(x: int) -> int:
    return x + 1


def keep(x: int) -> int:
    return 0


#@ no_exception \all
def f(k: int, xs: List[int], d: Dict[str, int]) -> int:
    n = 0
    for i in range(3):
        n += 1
    return h(len(range(2)))


#@ no_exception \all
def g(xs: List[int], d: Dict[str, int]) -> int:
    return 1 if len(d) < 3 else 0


#@ no_exception \all
def r(k: int) -> int:
    return gi(1)


#@ no_exception \all
def u(xs: List[int]) -> int:
    return keep(xs.copy())


if __name__ == "__main__":
    print(f(1, [1], {"a": 1}), g([1], {"a": 1}), r(0), u([1]))
