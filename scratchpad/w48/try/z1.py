#@ requires 0 <= a <= 3
#@ ensures 0 <= \result <= 3
#@ assigns \nothing
def f(a: int) -> int:
    return a
