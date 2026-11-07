#@ ensures \result == 1
def f() -> int:
    x: int = 1

    def g() -> int:
        return 7
    x = 2
    return x
