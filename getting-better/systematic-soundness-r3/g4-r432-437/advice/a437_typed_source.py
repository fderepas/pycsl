# advice probe (route #437): witness 6537 sorting values declared `List[int]`
from typing import List


#@ no_exception \all
def f(xs: List[int]) -> int:
    ys = sorted(xs)
    return len(ys)
