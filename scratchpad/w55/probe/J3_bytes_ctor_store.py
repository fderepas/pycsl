# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    b = bytes([1, 2])
    b[0] = 9
    return b[0]
