from typing import List


#@ requires n >= 0
#@ no_exception \all
def a(n: int) -> int:
    s = n * "a"
    return 0


#@ requires n >= 0
#@ no_exception \all
def b(n: int) -> int:
    xs = n * [0]
    return 0


#@ requires n >= 0
#@ no_exception \all
def c(n: int) -> int:
    t = (1,) * n
    return 0


#@ requires n >= 0
#@ no_exception \all
def d(n: int) -> int:
    t = b"a" * n
    return 0


#@ requires n >= 0
#@ no_exception \all
def e(xs: List[int], n: int) -> int:
    ys = xs * n
    return 0


#@ requires n >= 0
#@ no_exception \all
def g(n: int) -> int:
    xs = list(range(n))
    return 0


#@ ensures \result == 6
def h() -> int:
    xs = [1, 2] * 3
    return len(xs)
