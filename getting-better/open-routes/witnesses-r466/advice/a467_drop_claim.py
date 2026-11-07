"""Advice probe (route #467): '... or drop the exception from this function's claim' -- witness
7270 without `#@ no_exception`. VERIFIES (nothing claims the call does not raise)."""
from x1_hd467 import g


#@ ensures True
def f(n: int) -> int:
    return g(n)
