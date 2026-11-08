# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception ValueError
#@ ensures True
#@ assigns \nothing
def f() -> int:
    return int("abc")
