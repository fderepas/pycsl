#@ requires a == 1
#@ requires b == 3
#@ ensures \result > 0.3333333333333333
#@ assigns \nothing
def f(a: int, b: int) -> float:
    return a / b
