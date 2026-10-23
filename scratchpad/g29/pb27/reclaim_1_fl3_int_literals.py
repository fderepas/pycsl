_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    a: int = 0x10
    b: int = 1_000
    return a + b
