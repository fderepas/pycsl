#@ requires b == False
#@ ensures \result == 0
#@ assigns \nothing
def f(b: bool) -> int:
    if b is True:
        return 7
    return 0
