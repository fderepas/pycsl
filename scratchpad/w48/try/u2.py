#@ requires a == b == c
#@ ensures \result == 7
#@ assigns \nothing
def f(a: bool, b: bool, c: bool) -> int:
    if a == b and b == c:
        return 7
    return 0
