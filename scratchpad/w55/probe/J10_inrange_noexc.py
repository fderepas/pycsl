# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    b = bytearray([1])
    b[0] = 9
    return b[0]
