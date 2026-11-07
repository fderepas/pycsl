# pycsl-flags: --memory-model hoare

#@ requires True
#@ bounded_int 8
#@ ensures \result == 300
#@ assigns \nothing
def f() -> int:
    return 300
