# pycsl-flags: --memory-model hoare

#@ requires True
#@ ensures \result == a + b
#@ assigns \nothing
def f(a: str, b: str) -> str:
    s = a + b
    return s
