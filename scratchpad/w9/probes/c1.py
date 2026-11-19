_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result >= 0
def f(n: int) -> int:
    i = 0
    #@ loop invariant i == 99
    #@ loop variant n - i
    while i < n:
        i = i + 1
    return i
