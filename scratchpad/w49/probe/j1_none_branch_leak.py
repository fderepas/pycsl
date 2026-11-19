#@ requires c > 0
#@ ensures \result == 7
#@ assigns \nothing
def f(c: int) -> int:
    if c > 0:
        x = None
    else:
        x = 5
    if x == 0:
        return 7
    return 0
