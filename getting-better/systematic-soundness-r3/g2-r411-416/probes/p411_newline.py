#@ requires s == "\n"
#@ ensures \result == 4
def f(s: str) -> int:
    return len(s)


#@ requires s == "a\"b"
#@ ensures \result == 6
def g(s: str) -> int:
    return len(s)


#@ requires s == "é"
#@ ensures \result == 8
def h(s: str) -> int:
    return len(s)
