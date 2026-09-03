#@ ensures \result == 1
def outer() -> int:
    x: int = 1
    def inner() -> None:
        nonlocal x
        x = 2
    inner()
    return x
