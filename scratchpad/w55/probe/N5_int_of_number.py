# pycsl-flags: --memory-model hoare

#@ no_exception ValueError
#@ ensures True
#@ assigns \nothing
def f(a: int) -> int:
    return int(a)
