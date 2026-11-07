# pycsl-flags: --memory-model hoare
_ = 0
#@ requires c > 0
#@ ensures \result == 7
#@ assigns \nothing
def f(c: int) -> int:
    s: str = "ab"
    if c > 0:
        s = "abcd"
    if len(s) == 2:
        return 7
    return 0
