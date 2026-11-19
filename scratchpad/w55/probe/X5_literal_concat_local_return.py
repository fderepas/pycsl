# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == "ab"
#@ assigns \nothing
def f() -> str:
    s = "a" + "b"
    return s
