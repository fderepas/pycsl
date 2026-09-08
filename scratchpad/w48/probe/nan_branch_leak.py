#@ requires c > 0
#@ ensures \result == 7
#@ assigns \nothing
def f(c: int) -> int:
    if c > 0:
        x = float("nan")
    else:
        x = 1.0
    if x == x:
        return 7
    return 0
