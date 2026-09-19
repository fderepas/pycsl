from typing import List
_ = 0  # anchor


#@ requires \forall i: int; 0 <= i and i < 2 ==> xs[i] == 1
#@ ensures \result == -1
def f(xs: List[int]) -> int:
    return xs[0]


#@ ensures \result == -1
def probe() -> int:
    ys: List[int] = [5, 5]
    return f(ys)
