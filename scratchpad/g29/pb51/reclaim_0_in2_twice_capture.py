_ = 0  # anchor


def add(a: int, b: int) -> int:
    return a + b


#@ ensures \result == 0
def probe() -> int:
    return add(1, 1) + add(1, 2)
