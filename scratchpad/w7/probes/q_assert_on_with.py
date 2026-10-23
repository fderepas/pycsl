#@ ensures \result == 0
def f() -> int:
    #@ assert 1 == 2
    if True:
        pass
    return 0
