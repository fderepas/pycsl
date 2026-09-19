_ = 0  # anchor


#@ ensures \result == -1
# an ordinary comment between the block and the def
def f() -> int:
    return 0


#@ ensures \result == -1
def probe() -> int:
    return f()
