_ = 0  # anchor


#@ \diverges
#@ ensures \result == 5
def spin(n: int) -> int:
    while n > 0:
        n = n + 1
    return 0


#@ ensures \result == 5
def probe() -> int:
    return spin(0)
