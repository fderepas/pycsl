_ = 0  # anchor


#@ \trusted
#@ ensures \result == 99
def t() -> int:
    return 1


#@ ensures \result == 99
def f() -> int:
    return 0


#@ ensures \result == 99
def probe() -> int:
    return f()
