#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def helper(a: list) -> int:
    a[0] = 7
    return 0

#@ requires \length(xs) == 2
#@ ensures \result == 0
#@ assigns \nothing
def driver(xs: list) -> int:
    xs[0] = 0
    h = helper(xs)
    return xs[0]
