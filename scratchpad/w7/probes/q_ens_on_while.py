#@ ensures \result == 0
def f() -> int:
    i: int = 0
    #@ ensures 1 == 2
    #@ loop invariant i >= 0
    #@ loop variant 3 - i
    while i < 3:
        i = i + 1
    return 0
