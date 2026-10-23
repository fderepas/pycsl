_ = 0  # anchor


#@ ensures \result == 1.0
def probe() -> float:
    a: float = 0.1
    b: float = 0.2
    c: float = 0.7
    return a + b + c
