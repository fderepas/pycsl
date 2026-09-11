# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    a = [1, 2, 3]
    b = a[0:10]
    return len(b)
