"""Advice probe (route #468, PYCSL-R468-VAL-LIST-LENGTH): 'Write only the list's elements in the
callee (`x[i] = v`), or drop the length change from it' -- witness 7275's helper `x.append(1)`
replaced by `x[0] = 1`. VERIFIES."""
from typing import List
from x1_he468 import g


#@ requires \length(a) == 2
#@ ensures \result == 2
def f(a: List[int]) -> int:
    g(a)
    return len(a)
