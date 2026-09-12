#@ ensures \result == 0
def f() -> int:
    y: bool = 1
    if y is True:
        return 1
    return 0
