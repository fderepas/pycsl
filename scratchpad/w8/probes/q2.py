#@ requires n >= 0
#@ ensures \result == 2
def f(n: int) -> int:
    if (n
#@ assert 1 == 2
            >= 0):
        return 2
    return 2
