# pycsl-expected: PASS
#@ ensures \result == 1
def f1() -> int:
    t = "é"
    return len(t)


#@ requires s == "\n"
#@ ensures \result == 1
def f2(s: str) -> int:
    return len(s)


#@ requires s == "a\"b"
#@ ensures \result == 3
def f3(s: str) -> int:
    return len(s)


#@ requires s == "a\\b"
#@ ensures \result == 3
def f4(s: str) -> int:
    return len(s)


#@ ensures \result == True
def f5(s: str) -> bool:
    t = "é" + s
    return len(t) == len(s) + 1


#@ requires s == "é"
#@ no_exception \all
def f6(s: str) -> str:
    return s[0]


#@ ensures \result == 2
def f7() -> int:
    t = "x\t"
    return len(t)


#@ ensures \result == True
def f8() -> bool:
    t = "\n"
    u = "\r"
    return t != u
