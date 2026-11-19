#@ requires c > 0
#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    if c > 0:
        x = None
    else:
        x = 5
    return x + 1
