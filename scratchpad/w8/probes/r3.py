#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    xs = [1, 2, 3]
    return xs.count(2)
