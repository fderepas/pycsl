def g(x: bool) -> int:
    if x is True:
        return 1
    return 0

#@ ensures \result == 1
def f() -> int:
    return g(True)
