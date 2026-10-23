#@ requires True
#@ ensures \result == a + b
#@ assigns \nothing
def g(a: int, b: int = 3) -> int:
    return a + b

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver() -> int:
    return g(a=2, b=4)
