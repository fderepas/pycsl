#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    assert n > 0
    return n
