#@ ensures \result == 2
def f() -> int:
    x: int = 1
    return (
#@ ghost x = 99
#@ assert x == 99
        2)
