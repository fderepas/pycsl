# pycsl-flags: --memory-model hoare

_N: int = 1


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    global _N
    _N = 2
    return _N
