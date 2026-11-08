#@ ensures \result == 1
def probe() -> int:
    sl = slice(0, 2)
    if sl == 0:
        return 1
    return 2
