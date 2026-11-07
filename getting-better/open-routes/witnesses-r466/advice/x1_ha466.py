"""Advice probe helper (route #466): witness 7260's `X = 1 // 0` rewritten so that it cannot raise."""
X = 1 // 1


#@ ensures \result == x + 1
def g(x: int) -> int:
    return x + 1
