# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    s: str = "\U0001F600"
    return len(s)
