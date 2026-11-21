"""Helper for routes #122/#124 witnesses: an `inc` that DECREMENTS."""


#@ ensures \result == y - 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y - 1
