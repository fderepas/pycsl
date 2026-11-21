"""Advice probe (route #466, PYCSL-R466-IMPORTED-MODULE-RAISES): 'Rewrite the module's top level so
that it cannot raise' -- witness 7260's helper `X = 1 // 0` rewritten `X = 1 // 1`. VERIFIES."""
from x1_ha466 import g


#@ no_exception \all
#@ ensures \result == n + 1
def f(n: int) -> int:
    return g(n)
