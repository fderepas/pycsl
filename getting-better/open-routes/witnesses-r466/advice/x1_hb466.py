"""Advice probe helper (route #466): witness 7267's `g` bound UNCONDITIONALLY at the top level."""


#@ ensures \result == x
def g(x: int) -> int:
    return x
