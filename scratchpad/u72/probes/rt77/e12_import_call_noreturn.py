import rt77lib_nr


#@ requires x > 0 and x < 0
#@ ensures \result == 99
def stop(x: int) -> int:
    return 1


#@ requires z > 5
#@ ensures \result == 0
def use(z: int) -> int:
    rt77lib_nr.stop(z)
    return 0
