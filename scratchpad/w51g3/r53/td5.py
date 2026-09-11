#@ requires a == 2
#@ requires b == 3
#@ ensures \result == 0.6666666666666666
#@ assigns \nothing
def f(a: int, b: int) -> float:
    return a / b
