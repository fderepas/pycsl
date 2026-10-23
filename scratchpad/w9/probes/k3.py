_ = 0  # anchor
#@ requires \length(a) >= 2
#@ ensures \result == 0
#@ assigns \nothing
def f(a: list) -> int:
    b = a[0:2]
    c = len(b)
    if c:
        return 7
    return 0
