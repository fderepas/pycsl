_ = 0  # anchor


def sq(x: int) -> int:
    return x * x


#@ ensures \result == 99
def probe() -> int:
    s: int = 0
    i: int = 0
    #@ loop variant 3 - i
    while i < 3:
        s = s + sq(i)
        i = i + 1
    return s
