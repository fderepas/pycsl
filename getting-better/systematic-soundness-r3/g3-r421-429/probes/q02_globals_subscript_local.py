K = [1]


#@ no_exception \all
def f() -> int:
    s = {globals()["K"]}
    return len(s)
