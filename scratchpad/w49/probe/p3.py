# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    s = {1, 2, 3}
    if 1 in s:
        return 0
    return 7
