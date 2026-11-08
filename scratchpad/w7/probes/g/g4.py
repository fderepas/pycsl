#@ requires n >= 0
#@ ensures \result >= 100
#@ assigns \nothing
def f(n: int) -> int:
    i: int = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        i = i + 1
    return i
