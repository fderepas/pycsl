from zqf75 import one

L = [1]


#@ ensures \result == 1
def f() -> int:
    one()
    return len(L)
