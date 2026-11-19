# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures \result == 999
#@ assigns \nothing
def f() -> int:
    b = bytearray([1])
    b[0] = 999
    return b[0]
