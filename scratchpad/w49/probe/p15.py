# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    i = 0
    #@ loop invariant i >= 0
    while i >= 0:
        i = i + 1
    return 0
