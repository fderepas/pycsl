# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = (i for i in range(1))
    y = (i for i in range(2))
    if x == y:
        return 7
    return 0
