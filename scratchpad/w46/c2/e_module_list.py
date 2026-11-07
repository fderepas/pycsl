_ = 0  # anchor
gl = [1, 2, 3]


#@ assigns \nothing
def g() -> int:
    gl[0] = 9
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    _r = g()
    return gl[0]
