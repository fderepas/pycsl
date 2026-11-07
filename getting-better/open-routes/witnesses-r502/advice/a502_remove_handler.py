# Route #502 advice probe (u5): witness 7956 with the handler removed ("drop them from this context").
from typing import List

#@ ensures \result == 1
def g(xs: List[int]) -> int:
    ys = [10 // v for v in xs]
    return 1


#@ ensures \result == 1
def f(xs: List[int]) -> int:
    return g(xs)
