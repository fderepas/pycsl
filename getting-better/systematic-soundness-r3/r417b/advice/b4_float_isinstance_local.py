#@ requires -100 < n and n < 100
#@ no_exception \all
def f(n: int) -> int:
    y = float(n)
    if isinstance(y, float):
        return 1
    return 0
