# pycsl-flags: --memory-model hoare

#@ requires True
#@ ensures \result == len(a) + len(b)
#@ assigns \nothing
def f(a: str, b: str) -> int:
    s = a + b
    return len(s)
