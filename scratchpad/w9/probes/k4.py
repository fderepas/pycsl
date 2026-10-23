_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    s = ""
    t = f"{s}"
    if t:
        return 7
    return 0
