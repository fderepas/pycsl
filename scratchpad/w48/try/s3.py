#@ requires \length(a) == 4
#@ ensures \result == 0
#@ assigns \nothing
def f(a: list) -> int:
    if len(a) == 4 and abs(-4) == 4:
        return 0
    return 1
