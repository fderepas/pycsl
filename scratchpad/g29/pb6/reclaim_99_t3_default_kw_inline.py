_ = 0  # anchor


def f(x: int, y: int = 2) -> int:
    return x * 10 + y


#@ ensures \result == 99
def probe() -> int:
    return f(1) + f(3, y=4)
