# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    d = {"a": 10, "\x61": 20}
    return len(d)
