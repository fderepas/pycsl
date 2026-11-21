g: int = 0

#@ requires True
#@ ensures True
#@ assigns \nothing
def setter() -> None:
    global g
    g = 5

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver() -> int:
    setter()
    return g
