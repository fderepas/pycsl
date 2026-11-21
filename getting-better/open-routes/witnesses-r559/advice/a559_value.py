# advice probe (route #559): witness do1232 following the advice -- store the value you mean
from typing import List


#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    ys = [k]
    return ys[0] + 1
