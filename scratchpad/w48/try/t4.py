#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= 3
    #@ loop invariant total == i
    #@ loop variant 3 - i
    while i < 3:
        total = total + 1
        i = i + 1
    if total == 3:
        return 0
    return 1
