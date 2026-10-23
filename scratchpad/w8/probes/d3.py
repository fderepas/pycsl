#@ requires True
#@ ensures \result == a + b
#@ assigns \nothing
def g(a: int, b: int = 3) -> int:
    return a + b

#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def driver() -> int:
    return g(2, b=0)
