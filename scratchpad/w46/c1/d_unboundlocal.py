_ = 0  # anchor
g_v = 5


#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    if g_v == 5:
        return g_v
    g_v = 1
    return 0
