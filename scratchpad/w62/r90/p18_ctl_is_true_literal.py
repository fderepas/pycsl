#@ ensures \result == 1
def f() -> int:
    y = True
    if y is True:
        return 1
    return 0
