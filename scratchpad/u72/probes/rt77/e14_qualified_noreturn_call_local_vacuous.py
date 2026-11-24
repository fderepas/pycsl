import rt77lib_nr


#@ requires x > 0 and x < 0
#@ ensures \result == 99
def stop(x: int) -> int:
    return 1


#@ ensures \result == 0
def use(z: int) -> int:
    if z > 0 and z < 0:
        rt77lib_nr.stop(z)
    return 0
