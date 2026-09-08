# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    a: str = "a"
    b: str = a + "b"
    c: str = "ab"
    if b is c:
        return 7
    return 0
