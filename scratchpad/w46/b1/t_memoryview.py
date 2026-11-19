_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = memoryview(b"ab")
    if x:
        return 7
    return 0
