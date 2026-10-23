# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 10
#@ assigns \nothing
def f() -> int:
    s: str = "abc"
    t: str = s[0:10]
    return len(t)
