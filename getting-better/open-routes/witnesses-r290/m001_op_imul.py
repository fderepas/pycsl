from typing import List, Set
import operator

#@ requires \length(xs) == 2
#@ ensures \result == 1
#@ assigns \nothing
def g(xs: List[int]) -> int:
    operator.imul(xs, 2)
    return 1

#@ ensures \result == 23
def f() -> int:
    xs: List[int] = [3, 1]
    g(xs)
    return len(xs) * 10 + xs[0]

if __name__ == "__main__":
    assert f() == 23, f()
