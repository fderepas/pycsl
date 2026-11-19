r"""Test 6691 -- route #441 (expected PASS): CONTROL: builtin calls matching their signature rows with DERIVED arguments (`len` of a list / str, `abs` / `int` of an int, `bool` of an int, `isinstance` with a builtin class, `min` of two ints, `range(n)`), each under `#@ no_exception \all`. Admitted; PROVED at candidate (CPython ok).
"""
# pycsl-expected: PASS
from typing import List


#@ no_exception \all
def f1(xs: List[int], s: str) -> int:
    return len(xs) + len(s)


#@ no_exception \all
def f2(n: int) -> int:
    return abs(n) + int(n)


#@ no_exception \all
def f3(s: str) -> bool:
    return isinstance(s, str) and bool(len(s))


#@ no_exception \all
def f4(n: int) -> int:
    k = 0
    for i in range(n):
        k = k + i
    return k + min(1, 2)


if __name__ == "__main__":
    print(f1([1, 2], "ab"), f2(-3), f3("a"), f4(3))
