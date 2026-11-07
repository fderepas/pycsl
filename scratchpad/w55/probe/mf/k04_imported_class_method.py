# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from multi_file_lib.probecls import Helper


#@ requires True
#@ ensures \result > 0
#@ assigns \nothing
def f(h: Helper) -> int:
    return h.pos_only(-5)
