#@ requires \length(a) == 5
#@ ensures \result == 0
#@ assigns \nothing
def f(a: list) -> int:
    b = a[1:4]
    if len(b) == 3:
        return 0
    return 1
