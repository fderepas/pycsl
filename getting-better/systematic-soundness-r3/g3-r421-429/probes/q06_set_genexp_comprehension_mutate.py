from typing import Set


#@ no_exception \all
def f(s: Set[int]) -> int:
    n = sum(1 for x in s if s.add(x + 100) is None)
    return n
