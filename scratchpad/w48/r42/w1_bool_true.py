#@ requires b == True
#@ ensures \result == 7
#@ assigns \nothing
def f(b: bool) -> int:
    if b is True:
        return 7
    return 0
