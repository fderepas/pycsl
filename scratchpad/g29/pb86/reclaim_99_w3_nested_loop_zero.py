_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    s: int = 0
    for i in range(2):
        for j in range(2):
            s = s + 1
    return s
