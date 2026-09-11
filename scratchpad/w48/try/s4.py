#@ requires \length(a) == 4
#@ ensures \result == 0
#@ assigns \nothing
def f(a: list) -> int:
    n = len(a)
    m = abs(-4)
    if n == 4 and m == 4:
        return 0
    return 1
