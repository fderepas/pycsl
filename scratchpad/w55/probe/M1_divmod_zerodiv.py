# pycsl-flags: --memory-model hoare

#@ no_exception ZeroDivisionError
#@ ensures True
#@ assigns \nothing
def f(a: int) -> int:
    q = divmod(a, 0)[0]
    return q
