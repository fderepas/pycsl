from lib import C

#@ requires True
#@ ensures \result == 99
#@ assigns \nothing
def driver() -> int:
    c = C()
    return c.x
