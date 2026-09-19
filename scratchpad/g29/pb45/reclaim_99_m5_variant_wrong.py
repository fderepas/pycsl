_ = 0  # anchor


#@ \variant n
#@ ensures \result == 99
def down(n: int) -> int:
    if n <= 0:
        return 0
    return down(n + 1)


#@ ensures \result == 99
def probe() -> int:
    return down(0) + 1
