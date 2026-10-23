# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from multi_file_lib.probelib import pos_only


#@ ensures \result > 0
#@ assigns \nothing
def f() -> int:
    return pos_only(-5)
