_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = 0
    i = 0
    while i < 3:
        try:
            i = i + 1
        finally:
            break
    return i - 1
