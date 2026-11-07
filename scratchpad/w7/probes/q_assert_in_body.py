#@ ensures \result == 0
def f() -> int:
    x: int = 0
    #@ assert 1 == 2
    x = 0
    return x
