# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    s = {1, 2}
    s.add(3)
    return len(s)
