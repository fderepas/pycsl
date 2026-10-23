from typing import List


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs = [1, 2, 3]
    return xs[0]
