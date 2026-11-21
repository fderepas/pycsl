# pycsl-flags: --memory-model hoare

_N: int = 1


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return _N
