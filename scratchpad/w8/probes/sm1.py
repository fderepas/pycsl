from typing import List

#@ requires \length(a) == 2 and a[0] == 1 and a[1] == 2
#@ ensures \sum(a, 0, 2) == 0
#@ assigns \nothing
def f(a: List[int]) -> int:
    return 0
