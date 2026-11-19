#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return 0
#@ ghost z = 1
