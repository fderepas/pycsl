_ = 0  # anchor


#@ \trusted
#@ ensures \result == 1
def t() -> int:
    return 1


#@ ensures \result == 7
def f() -> int:
    return 0


#@ ensures \result == 7
def probe() -> int:
    return f()
