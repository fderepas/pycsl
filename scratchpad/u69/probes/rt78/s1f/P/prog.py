from depf78 import g


#@ ensures \result == 1
def h() -> int:
    return g()


print("result", h())
