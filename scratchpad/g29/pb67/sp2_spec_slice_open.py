_ = 0  # anchor


#@ requires s == "abc"
#@ ensures \result == \length(s[1:])
def probe(s: str) -> int:
    return 0
