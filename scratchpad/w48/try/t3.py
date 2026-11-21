#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    total = 0
    #@ loop invariant 0 <= i <= 3
    #@ loop variant 3 - i
    for i in range(3):
        total = total + 1
    if total == 3:
        return 0
    return 1
