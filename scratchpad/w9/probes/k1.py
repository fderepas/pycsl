_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def g(x: int) -> int:
    if x:
        return 7
    return 0

#@ requires \length(a) >= 2
#@ ensures \result == 0
#@ assigns \nothing
def f(a: list) -> int:
    return g(sorted(a))
