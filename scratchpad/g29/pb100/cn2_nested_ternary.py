_ = 0  # anchor


#@ ensures \result == 0
def probe(a: int) -> int:
    return 1 if a > 0 else (2 if a == 0 else 3)
