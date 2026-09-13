import ctypes

#@ \trusted
#@ ensures \result == 0
def helper() -> int:
    return 0

#@ ensures \result == 5
def f() -> int:
    return 5
