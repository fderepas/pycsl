#@ ensures \result == 1
def f() -> int:
    x: int = 1
    class C:
        pass
    x = 2
    return x
