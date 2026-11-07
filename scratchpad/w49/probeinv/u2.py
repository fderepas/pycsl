# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s: str = "\U0001F600"
    return len(s)
