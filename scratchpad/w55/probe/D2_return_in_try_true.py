# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    try:
        return 5
    except Exception:
        return 9
