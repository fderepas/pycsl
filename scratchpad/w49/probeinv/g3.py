# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    a = [1, 2, 3]
    b = a[0:10]
    if len(b) == 10:
        return 7
    return 0
