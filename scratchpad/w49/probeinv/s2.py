# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    a = [1, 2]
    b = [1, 2]
    if a is b:
        return 7
    return 0
