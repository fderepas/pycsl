#@ requires n >= 0
#@ ensures \exists i: int; (0 <= i and i < 2 and \result == i + 5)
#@ assigns \nothing
def f(n: int) -> int:
    return 0
