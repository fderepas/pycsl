_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    #@ ghost int g = 7
    x = 0
    return x
