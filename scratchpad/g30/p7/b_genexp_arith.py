#@ ensures \result == 5
def probe() -> int:
    g = (x for x in [1, 2, 3])
    return g + 5
