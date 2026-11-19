# pycsl-flags: --memory-model hoare
_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    s = "ab"
    t = s[5:6]
    return len(t)
