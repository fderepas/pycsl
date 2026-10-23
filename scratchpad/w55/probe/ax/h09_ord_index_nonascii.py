# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result < 256
#@ assigns \nothing
def f() -> int:
    s = "€"
    return ord(s[0])
