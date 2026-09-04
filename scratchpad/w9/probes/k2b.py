_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    d = {}
    d[1] = 7
    v = d.get(1, 0)
    if v:
        return 7
    return 0
