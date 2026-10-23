_ = 0  # anchor


#@ ensures \result == 99
# an ordinary comment between the block and the def
def f() -> int:
    return 0


#@ ensures \result == 99
def probe() -> int:
    return f()
