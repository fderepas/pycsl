# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires x > 0
#@ ensures \result > 0
#@ assigns \nothing
def pos_only(x: int) -> int:
    return x


#@ ensures \result > 0
#@ assigns \nothing
def f() -> int:
    return pos_only(-5)
