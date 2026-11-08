#@ ensures True
def f() -> int:
    s = "a" + "b"
    return len(s)
