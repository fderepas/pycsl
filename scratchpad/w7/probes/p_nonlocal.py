#@ ensures \result == 1
def f() -> int:
    x: int = 1
    import os
    x = 2
    return x
