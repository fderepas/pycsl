# pycsl-flags: --memory-model hoare
_ = 0
#@ requires True
#@ ensures True
#@ assigns \nothing
def f() -> int:
    s = "ab"
    parts = s.split("")
    return 0
