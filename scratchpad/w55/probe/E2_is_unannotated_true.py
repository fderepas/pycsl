# pycsl-flags: --memory-model hoare

#@ requires a == "a"
#@ ensures \result == 0
#@ assigns \nothing
def f(a: str) -> int:
    b = a + "b"
    c = "ab"
    if b is c:
        return 7
    return 0
