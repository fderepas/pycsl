g: int = 0

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def sneaky() -> int:
    return 0

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver() -> int:
    return sneaky()
