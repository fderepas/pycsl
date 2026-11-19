# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    b = bytearray([1, 2])
    b[0] = 9
    return b[0]
