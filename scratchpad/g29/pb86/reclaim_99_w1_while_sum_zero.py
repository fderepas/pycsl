_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    i: int = 0
    s: int = 0
    #@ loop variant 3 - i
    while i < 3:
        s = s + 2
        i = i + 1
    return s
