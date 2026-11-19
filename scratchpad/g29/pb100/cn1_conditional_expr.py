_ = 0  # anchor


#@ ensures \result == 0
def probe(flag: int) -> int:
    x: int = 5 if flag > 0 else 7
    return x
