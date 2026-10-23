#@ requires c <= 0
#@ ensures \result == 7
#@ assigns \nothing
def f(c: int) -> int:
    if c > 0:
        x = 5
    else:
        x = None
    if x == 0:
        return 7
    return 0
