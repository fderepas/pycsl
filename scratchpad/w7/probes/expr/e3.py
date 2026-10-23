#@ requires n >= 0
#@ ensures n > 0 ==> \result > 0
#@ ensures n == 0 ==> \result > 0
#@ assigns \nothing
def f(n: int) -> int:
    return n
