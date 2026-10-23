_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = 0
    try:
        x = 1
    except* ValueError:
        x = 7
    return x
