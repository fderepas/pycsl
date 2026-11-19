#@ ensures \result == 0
def probe() -> int:
    return sum(x for x in [3, 1, 2])
