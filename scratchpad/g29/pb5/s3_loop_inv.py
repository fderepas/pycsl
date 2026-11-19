_ = 0  # anchor


#@ ensures \result == 7
def probe() -> int:
    i: int = 0
    s: int = 0
    #@ loop invariant s == i
    #@ loop variant 3 - i
    while i < 3:
        s = s + 1
        i = i + 1
    return s
