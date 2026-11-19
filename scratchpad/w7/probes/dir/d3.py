#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
#@ \variant n
def rec(n: int) -> int:
    if n == 0:
        return 0
    return 1 + rec(n - 1)
