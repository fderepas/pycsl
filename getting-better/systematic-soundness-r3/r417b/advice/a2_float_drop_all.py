#@ ensures \result == n
#@ no_exception \all
def g(n: int) -> int:
    return n


def f(n: int) -> int:
    x = float(g(n))
    return 0
