import ctypes

#@ \trusted
#@ ensures \result == 0
def helper() -> int:
    return 0

#@ ensures \result == 4
def f() -> int:
    return ctypes.sizeof(ctypes.c_int)
