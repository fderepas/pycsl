_ = 0  # anchor


#@ \trusted
#@ ensures \result == -1
def t() -> int:
    return 1


#@ ensures \result == -1
def f() -> int:
    return 0


#@ ensures \result == -1
def probe() -> int:
    return f()
