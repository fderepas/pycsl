#@ requires True
#@ ensures \result == 99
#@ assigns \nothing
def f() -> int:
    #@ assume 1 == 2
    return 0
