from typing import List

#@ requires True
#@ ensures \length(\result) == 2 and \result[0] == 9
#@ assigns \nothing
def g() -> List[int]:
    return [9, 9]

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    xs = g()
    return xs[0]
