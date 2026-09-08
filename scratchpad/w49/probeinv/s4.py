# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: str = "ab"
    if a is a:
        return 0
    return 7
