#@ requires n >= 0
#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    i: int = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        i = i + 1
    else:
        #@ assert 1 == 2
        i = 0
    return 0
