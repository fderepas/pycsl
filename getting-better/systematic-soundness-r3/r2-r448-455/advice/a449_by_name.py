# advice probe (route #449): witness 6954 with the parameter given by its name -- must VERIFY
from typing import List


def total(items: List[int], initial: int = 0) -> int:
    s = initial
    for x in items:
        s += x
    return s


#@ no_exception \all
def f(items: List[int]) -> int:
    return total(items, initial=1)
