#@ ensures \result == 1
def f() -> int:
    x: int = 1
    type Alias = int
    x = 2
    return x
