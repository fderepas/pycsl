#@ requires True
#@ ensures \result == 1 and (\result == 2 or \result == 1) and \result == 2
#@ assigns \nothing
def f() -> int:
    return 1
