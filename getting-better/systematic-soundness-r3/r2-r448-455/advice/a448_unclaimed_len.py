# advice probe (route #448): witness 6952 calling `len` with the argument it takes -- must VERIFY
from typing import List


def h(n: List[int]) -> int:
    return len(n)


#@ no_exception \all
def f(n: List[int]) -> int:
    return h(n)
