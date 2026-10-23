_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: int = 0
    for i in range(3):
        s = s + 2
    return s
