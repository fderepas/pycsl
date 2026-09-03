#@ ensures \result == 2
def f() -> int:
    return 2

y: int = (
    #@ assert 1 == 2
    1)
