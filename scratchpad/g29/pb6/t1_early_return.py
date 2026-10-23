_ = 0  # anchor


def pick(a: int) -> int:
    if a > 0:
        return 1
    return 2


#@ ensures \result == 4
def probe() -> int:
    return pick(5) + pick(-5)
