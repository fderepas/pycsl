#@ requires n >= 0
#@ ensures \result == 2
def f(n: int) -> int:
    while (n
#@ loop invariant 1 == 2
            > 100):
        n = n - 1
    return 2
