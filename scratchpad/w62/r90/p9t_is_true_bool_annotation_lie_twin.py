def g(x: bool) -> int:
    if x is True:
        return 1
    return 0

#@ ensures \result == 0
def f() -> int:
    return g(1)
