#@ no_exception \all
def f() -> int:
    k = str.maketrans("a", "b")
    s = {k}
    return len(s)
