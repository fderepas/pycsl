_ = 0  # anchor
#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    try:
        return 3
    finally:
        return 9
