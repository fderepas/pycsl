r"""uncaught int of float text"""
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    v = int("1.5")
    return v * 0 + 5
