_ = 0  # anchor


#@ ensures \result == 7
# an ordinary comment between the block and the def
def f() -> int:
    return 0


#@ ensures \result == 7
def probe() -> int:
    return f()
