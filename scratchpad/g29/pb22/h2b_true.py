_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    a: str = "k6404"
    b: str = "k44509"
    if a == b:
        return 1
    return 0
