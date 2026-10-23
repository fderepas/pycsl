_ = 0  # anchor


#@ requires i == 0 - 1
#@ ensures \result == 99
def probe(i: int) -> int:
    s: str = "abc"
    t: str = s[i:]
    return len(t)
