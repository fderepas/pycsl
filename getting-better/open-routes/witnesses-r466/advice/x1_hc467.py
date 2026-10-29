"""Advice probe helper (route #467): the imported function gets its OWN claim (its body proves it)."""


#@ no_exception \all
#@ requires x >= 0
#@ ensures \result == x
def g(x: int) -> int:
    assert x >= 0
    return x
