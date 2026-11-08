#@ ensures \result == 2
def f() -> int:
    return (
        #@ assert 1 == 2
        2)
