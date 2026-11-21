#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return 5 % 0
